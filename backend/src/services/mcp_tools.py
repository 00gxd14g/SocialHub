"""
MCP (Model Context Protocol) Tools for Social Media Management
Provides standardized tool interface for AI agents and external systems
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from ..models.unified_post import UnifiedPost, PlatformType, PostType, PostStatus
from ..models.user import User
from .platform_transformers import TransformerFactory, preview_transformed_content
from .queue_manager import queue_manager, create_post_job, create_analytics_job, JobPriority
from .enhanced_social_apis import social_api_manager, APICredentials
from .ai_content_service import AIContentService

logger = logging.getLogger(__name__)

class MCPToolResult:
    """Standardized result format for MCP tools"""
    
    def __init__(self, success: bool, data: Any = None, error: str = None, 
                 metadata: Dict[str, Any] = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }

class SocialPostTool:
    """MCP tool for creating and managing social media posts"""
    
    @staticmethod
    def create(user_id: int, content: str, platforms: List[str], 
               title: str = None, media_urls: List[str] = None,
               tags: List[str] = None, mentions: List[str] = None,
               links: List[str] = None, scheduled_time: str = None,
               post_type: str = "text", **kwargs) -> MCPToolResult:
        """
        Create a new social media post
        
        Args:
            user_id: ID of the user creating the post
            content: Main post content/caption
            platforms: List of platform names to publish to
            title: Optional title (for blog posts, LinkedIn articles)
            media_urls: List of media URLs to include
            tags: List of hashtags (without #)
            mentions: List of usernames to mention (without @)
            links: List of external links
            scheduled_time: ISO format datetime for scheduling
            post_type: Type of post (text, image, video, carousel, etc.)
        """
        try:
            # Validate user
            user = User.query.get(user_id)
            if not user:
                return MCPToolResult(False, error="User not found")
            
            # Validate platforms
            valid_platforms = []
            for platform_name in platforms:
                try:
                    platform = PlatformType(platform_name.lower())
                    valid_platforms.append(platform)
                except ValueError:
                    logger.warning(f"Invalid platform: {platform_name}")
            
            if not valid_platforms:
                return MCPToolResult(False, error="No valid platforms specified")
            
            # Parse scheduled time
            scheduled_dt = None
            if scheduled_time:
                try:
                    scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                except ValueError:
                    return MCPToolResult(False, error="Invalid scheduled_time format. Use ISO format.")
            
            # Create unified post
            unified_post = UnifiedPost(
                user_id=user_id,
                title=title,
                body=content,
                media_items=media_urls or [],
                tags=tags or [],
                mentions=mentions or [],
                links=links or [],
                post_type=PostType(post_type) if post_type else PostType.TEXT,
                target_platforms=[p.value for p in valid_platforms],
                scheduled_time=scheduled_dt,
                status=PostStatus.SCHEDULED if scheduled_dt else PostStatus.DRAFT
            )
            
            # Add to database
            from ..models.user import db
            db.session.add(unified_post)
            db.session.commit()
            
            # Preview content for all platforms
            previews = preview_transformed_content(unified_post, valid_platforms)
            
            # If scheduled, create queue jobs
            job_ids = []
            if scheduled_dt:
                for platform in valid_platforms:
                    job = create_post_job(
                        unified_post.id,
                        platform.value,
                        user_id,
                        scheduled_dt
                    )
                    job_id = queue_manager.enqueue(job)
                    job_ids.append(job_id)
            
            return MCPToolResult(
                True,
                data={
                    'post_id': unified_post.id,
                    'status': unified_post.status.value,
                    'platforms': [p.value for p in valid_platforms],
                    'scheduled_time': scheduled_dt.isoformat() if scheduled_dt else None,
                    'job_ids': job_ids,
                    'previews': previews
                },
                metadata={
                    'created_at': unified_post.created_at.isoformat(),
                    'idempotency_key': unified_post.idempotency_key
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            return MCPToolResult(False, error=str(e))
    
    @staticmethod
    def publish(post_id: int, platforms: List[str] = None) -> MCPToolResult:
        """
        Immediately publish a post to specified platforms
        
        Args:
            post_id: ID of the post to publish
            platforms: Optional list of platforms (defaults to all target platforms)
        """
        try:
            # Get post
            unified_post = UnifiedPost.query.get(post_id)
            if not unified_post:
                return MCPToolResult(False, error="Post not found")
            
            # Determine platforms to publish to
            if platforms:
                target_platforms = []
                for platform_name in platforms:
                    try:
                        platform = PlatformType(platform_name.lower())
                        if platform.value in unified_post.target_platforms:
                            target_platforms.append(platform)
                    except ValueError:
                        logger.warning(f"Invalid platform: {platform_name}")
            else:
                target_platforms = [PlatformType(p) for p in unified_post.target_platforms]
            
            if not target_platforms:
                return MCPToolResult(False, error="No valid platforms to publish to")
            
            # Create immediate publish jobs
            job_ids = []
            for platform in target_platforms:
                job = create_post_job(
                    unified_post.id,
                    platform.value,
                    unified_post.user_id,
                    priority=JobPriority.HIGH
                )
                job_id = queue_manager.enqueue(job)
                job_ids.append(job_id)
            
            # Update post status
            unified_post.status = PostStatus.QUEUED
            from ..models.user import db
            db.session.commit()
            
            return MCPToolResult(
                True,
                data={
                    'post_id': post_id,
                    'status': 'queued',
                    'platforms': [p.value for p in target_platforms],
                    'job_ids': job_ids
                }
            )
            
        except Exception as e:
            logger.error(f"Error publishing post: {str(e)}")
            return MCPToolResult(False, error=str(e))
    
    @staticmethod
    def get_status(post_id: int) -> MCPToolResult:
        """
        Get the status of a post and its platform-specific publications
        
        Args:
            post_id: ID of the post to check
        """
        try:
            unified_post = UnifiedPost.query.get(post_id)
            if not unified_post:
                return MCPToolResult(False, error="Post not found")
            
            # Get platform posts
            platform_statuses = []
            for platform_post in unified_post.platform_posts:
                platform_statuses.append({
                    'platform': platform_post.platform.value,
                    'status': platform_post.status.value,
                    'platform_post_id': platform_post.platform_post_id,
                    'platform_url': platform_post.platform_url,
                    'published_at': platform_post.published_at.isoformat() if platform_post.published_at else None,
                    'error_message': platform_post.error_message
                })
            
            return MCPToolResult(
                True,
                data={
                    'post_id': post_id,
                    'overall_status': unified_post.status.value,
                    'title': unified_post.title,
                    'body': unified_post.body[:100] + '...' if len(unified_post.body) > 100 else unified_post.body,
                    'scheduled_time': unified_post.scheduled_time.isoformat() if unified_post.scheduled_time else None,
                    'published_at': unified_post.published_at.isoformat() if unified_post.published_at else None,
                    'platform_statuses': platform_statuses,
                    'retry_count': unified_post.retry_count
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting post status: {str(e)}")
            return MCPToolResult(False, error=str(e))

class MediaUploadTool:
    """MCP tool for uploading and managing media"""
    
    @staticmethod
    def upload(user_id: int, media_url: str, media_type: str, 
               alt_text: str = None, caption: str = None) -> MCPToolResult:
        """
        Upload media for use in posts
        
        Args:
            user_id: ID of the user uploading media
            media_url: URL of the media to upload
            media_type: Type of media (image, video, gif)
            alt_text: Alternative text for accessibility
            caption: Caption for the media
        """
        try:
            # Validate user
            user = User.query.get(user_id)
            if not user:
                return MCPToolResult(False, error="User not found")
            
            # Create media item
            from ..models.unified_post import MediaItem
            media_item = MediaItem(
                original_url=media_url,
                media_type=media_type,
                alt_text=alt_text,
                caption=caption
            )
            
            # Add to database
            from ..models.user import db
            db.session.add(media_item)
            db.session.commit()
            
            return MCPToolResult(
                True,
                data={
                    'media_id': media_item.id,
                    'media_type': media_type,
                    'original_url': media_url,
                    'processing_status': media_item.processing_status
                }
            )
            
        except Exception as e:
            logger.error(f"Error uploading media: {str(e)}")
            return MCPToolResult(False, error=str(e))

class AnalyticsTool:
    """MCP tool for fetching and analyzing social media analytics"""
    
    @staticmethod
    def fetch(user_id: int, platforms: List[str] = None, 
              start_date: str = None, end_date: str = None) -> MCPToolResult:
        """
        Fetch analytics data for user's social media accounts
        
        Args:
            user_id: ID of the user
            platforms: List of platforms to fetch analytics for
            start_date: Start date in ISO format
            end_date: End date in ISO format
        """
        try:
            # Validate user
            user = User.query.get(user_id)
            if not user:
                return MCPToolResult(False, error="User not found")
            
            # Parse dates
            start_dt = None
            end_dt = None
            if start_date:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            # Default to last 30 days if no dates provided
            if not start_dt:
                start_dt = datetime.utcnow() - timedelta(days=30)
            if not end_dt:
                end_dt = datetime.utcnow()
            
            # Get analytics data
            from ..models.analytics import Analytics
            query = Analytics.query.filter(
                Analytics.user_id == user_id,
                Analytics.date_recorded >= start_dt.date(),
                Analytics.date_recorded <= end_dt.date()
            )
            
            if platforms:
                query = query.filter(Analytics.platform.in_(platforms))
            
            analytics_data = query.all()
            
            # Aggregate data
            platform_metrics = {}
            total_metrics = {
                'reach': 0,
                'impressions': 0,
                'likes': 0,
                'shares': 0,
                'comments': 0,
                'clicks': 0
            }
            
            for record in analytics_data:
                platform = record.platform
                if platform not in platform_metrics:
                    platform_metrics[platform] = {
                        'reach': 0,
                        'impressions': 0,
                        'likes': 0,
                        'shares': 0,
                        'comments': 0,
                        'clicks': 0
                    }
                
                metric_type = record.metric_type
                if metric_type in platform_metrics[platform]:
                    platform_metrics[platform][metric_type] += record.metric_value
                    total_metrics[metric_type] += record.metric_value
            
            return MCPToolResult(
                True,
                data={
                    'period': {
                        'start_date': start_dt.isoformat(),
                        'end_date': end_dt.isoformat()
                    },
                    'total_metrics': total_metrics,
                    'platform_metrics': platform_metrics,
                    'records_count': len(analytics_data)
                }
            )
            
        except Exception as e:
            logger.error(f"Error fetching analytics: {str(e)}")
            return MCPToolResult(False, error=str(e))
    
    @staticmethod
    def sync(user_id: int, platforms: List[str] = None) -> MCPToolResult:
        """
        Trigger analytics sync for user's connected accounts
        
        Args:
            user_id: ID of the user
            platforms: List of platforms to sync (defaults to all connected)
        """
        try:
            # Validate user
            user = User.query.get(user_id)
            if not user:
                return MCPToolResult(False, error="User not found")
            
            # Get connected accounts
            from ..models.social_account import SocialAccount
            accounts = SocialAccount.query.filter(
                SocialAccount.user_id == user_id,
                SocialAccount.is_active == True
            )
            
            if platforms:
                accounts = accounts.filter(SocialAccount.platform.in_(platforms))
            
            accounts = accounts.all()
            
            if not accounts:
                return MCPToolResult(False, error="No connected accounts found")
            
            # Create analytics sync jobs
            job_ids = []
            for account in accounts:
                job = create_analytics_job(
                    user_id,
                    account.platform,
                    datetime.utcnow()
                )
                job_id = queue_manager.enqueue(job)
                job_ids.append(job_id)
            
            return MCPToolResult(
                True,
                data={
                    'sync_jobs': job_ids,
                    'platforms': [account.platform for account in accounts],
                    'accounts_count': len(accounts)
                }
            )
            
        except Exception as e:
            logger.error(f"Error syncing analytics: {str(e)}")
            return MCPToolResult(False, error=str(e))

class ContentGenerationTool:
    """MCP tool for AI-powered content generation"""
    
    @staticmethod
    def generate_post(user_id: int, topic: str, platform: str = "twitter",
                     tone: str = "professional", length: str = "medium",
                     target_audience: str = None, keywords: List[str] = None) -> MCPToolResult:
        """
        Generate social media post content using AI
        
        Args:
            user_id: ID of the user
            topic: Topic or subject for the post
            platform: Target platform for optimization
            tone: Tone of voice (professional, casual, friendly, etc.)
            length: Content length (short, medium, long)
            target_audience: Description of target audience
            keywords: List of keywords to include
        """
        try:
            # Validate user
            user = User.query.get(user_id)
            if not user:
                return MCPToolResult(False, error="User not found")
            
            # Generate content using AI service
            ai_service = AIContentService()
            
            result = ai_service.generate_post_content(
                topic=topic,
                platform=platform,
                tone=tone,
                length=length,
                target_audience=target_audience,
                keywords=keywords or []
            )
            
            if not result.get('success'):
                return MCPToolResult(False, error=result.get('error', 'Content generation failed'))
            
            generated_content = result['generated_content']
            
            return MCPToolResult(
                True,
                data={
                    'content': generated_content['content'],
                    'hashtags': generated_content.get('hashtags', []),
                    'character_count': generated_content.get('character_count', 0),
                    'sentiment': generated_content.get('sentiment', 'neutral'),
                    'engagement_prediction': generated_content.get('engagement_prediction', 0),
                    'platform_optimized': platform,
                    'tone': tone,
                    'topic': topic
                },
                metadata={
                    'generation_time': datetime.utcnow().isoformat(),
                    'model_used': 'gpt-4',
                    'tokens_used': result.get('tokens_used', 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return MCPToolResult(False, error=str(e))
    
    @staticmethod
    def generate_hashtags(content: str, platform: str = "instagram", 
                         count: int = 10) -> MCPToolResult:
        """
        Generate relevant hashtags for content
        
        Args:
            content: Content to generate hashtags for
            platform: Target platform
            count: Number of hashtags to generate
        """
        try:
            ai_service = AIContentService()
            
            result = ai_service.generate_hashtags(
                content=content,
                platform=platform,
                count=count
            )
            
            if not result.get('success'):
                return MCPToolResult(False, error=result.get('error', 'Hashtag generation failed'))
            
            return MCPToolResult(
                True,
                data={
                    'hashtags': result['hashtags'],
                    'content_analyzed': content[:100] + '...' if len(content) > 100 else content,
                    'platform': platform,
                    'count_requested': count,
                    'count_generated': len(result['hashtags'])
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating hashtags: {str(e)}")
            return MCPToolResult(False, error=str(e))

class BlogPublishTool:
    """MCP tool for publishing blog posts"""
    
    @staticmethod
    def publish(user_id: int, title: str, content: str, platform: str = "medium",
               tags: List[str] = None, canonical_url: str = None) -> MCPToolResult:
        """
        Publish blog post to blogging platforms
        
        Args:
            user_id: ID of the user
            title: Blog post title
            content: Blog post content (Markdown supported)
            platform: Blogging platform (medium, wordpress, ghost)
            tags: List of tags
            canonical_url: Canonical URL for SEO
        """
        try:
            # Validate user
            user = User.query.get(user_id)
            if not user:
                return MCPToolResult(False, error="User not found")
            
            # Create unified post for blog
            unified_post = UnifiedPost(
                user_id=user_id,
                title=title,
                body=content,
                post_type=PostType.BLOG,
                tags=tags or [],
                target_platforms=[platform],
                status=PostStatus.DRAFT
            )
            
            # Add canonical URL if provided
            if canonical_url:
                unified_post.links = [canonical_url]
            
            # Add to database
            from ..models.user import db
            db.session.add(unified_post)
            db.session.commit()
            
            # Create publish job
            job = create_post_job(
                unified_post.id,
                platform,
                user_id,
                priority=JobPriority.NORMAL
            )
            job_id = queue_manager.enqueue(job)
            
            return MCPToolResult(
                True,
                data={
                    'post_id': unified_post.id,
                    'title': title,
                    'platform': platform,
                    'status': 'queued',
                    'job_id': job_id,
                    'word_count': len(content.split()),
                    'estimated_read_time': max(1, len(content.split()) // 200)  # ~200 WPM
                }
            )
            
        except Exception as e:
            logger.error(f"Error publishing blog post: {str(e)}")
            return MCPToolResult(False, error=str(e))

class MCPToolRegistry:
    """Registry for all MCP tools"""
    
    def __init__(self):
        self.tools = {
            # Social media posting
            'social.post.create': SocialPostTool.create,
            'social.post.publish': SocialPostTool.publish,
            'social.post.status': SocialPostTool.get_status,
            
            # Media management
            'social.media.upload': MediaUploadTool.upload,
            
            # Analytics
            'social.analytics.fetch': AnalyticsTool.fetch,
            'social.analytics.sync': AnalyticsTool.sync,
            
            # Content generation
            'social.content.generate': ContentGenerationTool.generate_post,
            'social.content.hashtags': ContentGenerationTool.generate_hashtags,
            
            # Blog publishing
            'blog.post.publish': BlogPublishTool.publish,
        }
    
    def execute(self, tool_name: str, **kwargs) -> MCPToolResult:
        """Execute a tool by name"""
        if tool_name not in self.tools:
            return MCPToolResult(False, error=f"Tool '{tool_name}' not found")
        
        try:
            tool_func = self.tools[tool_name]
            return tool_func(**kwargs)
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {str(e)}")
            return MCPToolResult(False, error=str(e))
    
    def list_tools(self) -> List[str]:
        """List all available tools"""
        return list(self.tools.keys())
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get schema for a specific tool"""
        schemas = {
            'social.post.create': {
                'description': 'Create a new social media post',
                'parameters': {
                    'user_id': {'type': 'integer', 'required': True},
                    'content': {'type': 'string', 'required': True},
                    'platforms': {'type': 'array', 'items': {'type': 'string'}, 'required': True},
                    'title': {'type': 'string', 'required': False},
                    'media_urls': {'type': 'array', 'items': {'type': 'string'}, 'required': False},
                    'tags': {'type': 'array', 'items': {'type': 'string'}, 'required': False},
                    'mentions': {'type': 'array', 'items': {'type': 'string'}, 'required': False},
                    'links': {'type': 'array', 'items': {'type': 'string'}, 'required': False},
                    'scheduled_time': {'type': 'string', 'format': 'datetime', 'required': False},
                    'post_type': {'type': 'string', 'enum': ['text', 'image', 'video', 'carousel'], 'required': False}
                }
            },
            'social.content.generate': {
                'description': 'Generate AI-powered social media content',
                'parameters': {
                    'user_id': {'type': 'integer', 'required': True},
                    'topic': {'type': 'string', 'required': True},
                    'platform': {'type': 'string', 'enum': ['twitter', 'instagram', 'facebook', 'linkedin'], 'required': False},
                    'tone': {'type': 'string', 'enum': ['professional', 'casual', 'friendly', 'humorous'], 'required': False},
                    'length': {'type': 'string', 'enum': ['short', 'medium', 'long'], 'required': False},
                    'target_audience': {'type': 'string', 'required': False},
                    'keywords': {'type': 'array', 'items': {'type': 'string'}, 'required': False}
                }
            }
            # Add more schemas as needed
        }
        
        return schemas.get(tool_name, {})

# Global MCP tool registry
mcp_registry = MCPToolRegistry()

