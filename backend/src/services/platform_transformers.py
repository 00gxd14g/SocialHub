"""
Platform-specific content transformers
Converts unified post schema to platform-specific formats
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse, urlencode
import logging

from ..models.unified_post import UnifiedPost, PlatformType, PostType

logger = logging.getLogger(__name__)

class BaseTransformer:
    """Base class for platform transformers"""
    
    def __init__(self, platform: PlatformType):
        self.platform = platform
        self.character_limit = 280  # Default, override in subclasses
        self.media_limit = 4
        self.hashtag_limit = 30
        self.mention_limit = 10
    
    def transform(self, unified_post: UnifiedPost) -> Dict[str, Any]:
        """Transform unified post to platform-specific format"""
        raise NotImplementedError("Subclasses must implement transform method")
    
    def validate_content(self, content: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate content against platform constraints"""
        errors = []
        
        # Check character limit
        text_length = len(content.get('text', ''))
        if text_length > self.character_limit:
            errors.append(f"Text exceeds {self.character_limit} character limit ({text_length} characters)")
        
        # Check media limit
        media_count = len(content.get('media', []))
        if media_count > self.media_limit:
            errors.append(f"Too many media items ({media_count}), limit is {self.media_limit}")
        
        # Check hashtag limit
        hashtag_count = len(content.get('hashtags', []))
        if hashtag_count > self.hashtag_limit:
            errors.append(f"Too many hashtags ({hashtag_count}), limit is {self.hashtag_limit}")
        
        return len(errors) == 0, errors
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract @mentions from text"""
        return re.findall(r'@(\w+)', text)
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract #hashtags from text"""
        return re.findall(r'#(\w+)', text)
    
    def add_utm_tracking(self, url: str, unified_post: UnifiedPost) -> str:
        """Add UTM parameters to URL"""
        return unified_post.add_utm_params(url, self.platform.value)

class TwitterTransformer(BaseTransformer):
    """Twitter/X platform transformer"""
    
    def __init__(self):
        super().__init__(PlatformType.TWITTER)
        self.character_limit = 280
        self.media_limit = 4
        self.hashtag_limit = 2  # Recommended for better engagement
        self.video_size_limit = 512 * 1024 * 1024  # 512MB
        self.image_size_limit = 5 * 1024 * 1024  # 5MB
    
    def transform(self, unified_post: UnifiedPost) -> Dict[str, Any]:
        """Transform to Twitter API v2 format"""
        content = unified_post.get_platform_content(self.platform)
        
        # Build tweet text
        tweet_text = self._build_tweet_text(unified_post)
        
        # Prepare media
        media_ids = []
        if unified_post.media_items:
            media_ids = self._prepare_media(unified_post.media_items)
        
        # Build tweet payload
        tweet_data = {
            'text': tweet_text
        }
        
        # Add media if present
        if media_ids:
            tweet_data['media'] = {
                'media_ids': media_ids
            }
        
        # Add location if present
        if unified_post.location:
            tweet_data['geo'] = {
                'place_id': unified_post.location.get('place_id')
            }
        
        # Add reply settings
        tweet_data['reply_settings'] = content.get('reply_settings', 'everyone')
        
        # Handle thread
        if unified_post.thread_parent_id:
            # This is part of a thread
            tweet_data['reply'] = {
                'in_reply_to_tweet_id': content.get('parent_tweet_id')
            }
        
        return {
            'endpoint': '/2/tweets',
            'method': 'POST',
            'data': tweet_data,
            'media_upload_required': len(media_ids) > 0,
            'estimated_length': len(tweet_text)
        }
    
    def _build_tweet_text(self, unified_post: UnifiedPost) -> str:
        """Build tweet text with proper formatting"""
        text_parts = []
        
        # Add title if present (for blog posts)
        if unified_post.title and unified_post.post_type == PostType.BLOG:
            text_parts.append(unified_post.title)
        
        # Add main body
        body = unified_post.body
        
        # Add links with UTM tracking
        for link in unified_post.links:
            tracked_link = self.add_utm_tracking(link, unified_post)
            body = body.replace(link, tracked_link)
        
        text_parts.append(body)
        
        # Add hashtags (limit to 2 for better engagement)
        hashtags = unified_post.tags[:self.hashtag_limit]
        if hashtags:
            hashtag_text = ' '.join([f'#{tag}' for tag in hashtags])
            text_parts.append(hashtag_text)
        
        # Join and truncate if necessary
        full_text = ' '.join(text_parts)
        
        if len(full_text) > self.character_limit:
            # Truncate and add ellipsis
            truncated = full_text[:self.character_limit - 3] + '...'
            return truncated
        
        return full_text
    
    def _prepare_media(self, media_items: List[Dict]) -> List[str]:
        """Prepare media for Twitter upload"""
        media_ids = []
        
        for item in media_items[:self.media_limit]:
            # This would be handled by the media upload service
            # For now, return placeholder IDs
            media_ids.append(f"media_{item.get('id', 'placeholder')}")
        
        return media_ids

class InstagramTransformer(BaseTransformer):
    """Instagram platform transformer"""
    
    def __init__(self):
        super().__init__(PlatformType.INSTAGRAM)
        self.character_limit = 2200
        self.media_limit = 10  # For carousels
        self.hashtag_limit = 30
        self.video_duration_limit = 60  # seconds for feed posts
        self.story_duration_limit = 15  # seconds for stories
    
    def transform(self, unified_post: UnifiedPost) -> Dict[str, Any]:
        """Transform to Instagram Graph API format"""
        content = unified_post.get_platform_content(self.platform)
        
        # Determine post type
        if unified_post.post_type == PostType.STORY:
            return self._transform_story(unified_post)
        elif unified_post.post_type == PostType.REEL:
            return self._transform_reel(unified_post)
        elif len(unified_post.media_items) > 1:
            return self._transform_carousel(unified_post)
        else:
            return self._transform_single_post(unified_post)
    
    def _transform_single_post(self, unified_post: UnifiedPost) -> Dict[str, Any]:
        """Transform single image/video post"""
        caption = self._build_caption(unified_post)
        
        container_data = {
            'caption': caption,
            'access_token': '{access_token}'  # Placeholder
        }
        
        # Add media
        if unified_post.media_items:
            media_item = unified_post.media_items[0]
            if media_item.get('media_type') == 'video':
                container_data['media_type'] = 'VIDEO'
                container_data['video_url'] = media_item.get('url')
            else:
                container_data['image_url'] = media_item.get('url')
        
        # Add location
        if unified_post.location:
            container_data['location_id'] = unified_post.location.get('instagram_location_id')
        
        # Add user tags
        if unified_post.mentions:
            user_tags = []
            for mention in unified_post.mentions:
                user_tags.append({
                    'username': mention.get('username'),
                    'x': mention.get('x', 0.5),  # Default center
                    'y': mention.get('y', 0.5)
                })
            container_data['user_tags'] = user_tags
        
        return {
            'endpoint': '/{ig-user-id}/media',
            'method': 'POST',
            'data': container_data,
            'requires_publish': True,
            'publish_endpoint': '/{ig-user-id}/media_publish'
        }
    
    def _transform_carousel(self, unified_post: UnifiedPost) -> Dict[str, Any]:
        """Transform carousel post"""
        caption = self._build_caption(unified_post)
        
        # Create children containers first
        children = []
        for media_item in unified_post.media_items[:self.media_limit]:
            child_data = {}
            if media_item.get('media_type') == 'video':
                child_data['media_type'] = 'VIDEO'
                child_data['video_url'] = media_item.get('url')
            else:
                child_data['image_url'] = media_item.get('url')
            
            children.append(child_data)
        
        container_data = {
            'media_type': 'CAROUSEL',
            'caption': caption,
            'children': children,
            'access_token': '{access_token}'
        }
        
        return {
            'endpoint': '/{ig-user-id}/media',
            'method': 'POST',
            'data': container_data,
            'requires_publish': True,
            'requires_children_creation': True
        }
    
    def _transform_story(self, unified_post: UnifiedPost) -> Dict[str, Any]:
        """Transform Instagram story"""
        story_data = {
            'media_type': 'STORIES',
            'access_token': '{access_token}'
        }
        
        if unified_post.media_items:
            media_item = unified_post.media_items[0]
            if media_item.get('media_type') == 'video':
                story_data['video_url'] = media_item.get('url')
            else:
                story_data['image_url'] = media_item.get('url')
        
        return {
            'endpoint': '/{ig-user-id}/media',
            'method': 'POST',
            'data': story_data,
            'requires_publish': True
        }
    
    def _transform_reel(self, unified_post: UnifiedPost) -> Dict[str, Any]:
        """Transform Instagram reel"""
        caption = self._build_caption(unified_post)
        
        reel_data = {
            'media_type': 'REELS',
            'video_url': unified_post.media_items[0].get('url') if unified_post.media_items else None,
            'caption': caption,
            'share_to_feed': True,
            'access_token': '{access_token}'
        }
        
        return {
            'endpoint': '/{ig-user-id}/media',
            'method': 'POST',
            'data': reel_data,
            'requires_publish': True
        }
    
    def _build_caption(self, unified_post: UnifiedPost) -> str:
        """Build Instagram caption"""
        caption_parts = []
        
        # Add main content
        if unified_post.body:
            caption_parts.append(unified_post.body)
        
        # Add links (Instagram doesn't make them clickable in captions)
        if unified_post.links:
            caption_parts.append("\n🔗 Links:")
            for link in unified_post.links:
                tracked_link = self.add_utm_tracking(link, unified_post)
                caption_parts.append(tracked_link)
        
        # Add hashtags
        if unified_post.tags:
            hashtags = unified_post.tags[:self.hashtag_limit]
            hashtag_text = ' '.join([f'#{tag}' for tag in hashtags])
            caption_parts.append(f"\n{hashtag_text}")
        
        caption = '\n'.join(caption_parts)
        
        # Truncate if necessary
        if len(caption) > self.character_limit:
            caption = caption[:self.character_limit - 3] + '...'
        
        return caption

class FacebookTransformer(BaseTransformer):
    """Facebook Pages transformer"""
    
    def __init__(self):
        super().__init__(PlatformType.FACEBOOK)
        self.character_limit = 63206  # Very high limit
        self.media_limit = 10
        self.hashtag_limit = 30
    
    def transform(self, unified_post: UnifiedPost) -> Dict[str, Any]:
        """Transform to Facebook Pages API format"""
        content = unified_post.get_platform_content(self.platform)
        
        # Build message
        message = self._build_message(unified_post)
        
        post_data = {
            'message': message,
            'access_token': '{access_token}'
        }
        
        # Add media
        if unified_post.media_items:
            if len(unified_post.media_items) == 1:
                # Single media post
                media_item = unified_post.media_items[0]
                if media_item.get('media_type') == 'video':
                    post_data['source'] = media_item.get('url')
                    return {
                        'endpoint': '/{page-id}/videos',
                        'method': 'POST',
                        'data': post_data
                    }
                else:
                    post_data['url'] = media_item.get('url')
                    return {
                        'endpoint': '/{page-id}/photos',
                        'method': 'POST',
                        'data': post_data
                    }
            else:
                # Multiple media - create album
                return self._create_album_post(unified_post, message)
        
        # Text-only post
        if unified_post.links:
            # Post with link
            post_data['link'] = self.add_utm_tracking(unified_post.links[0], unified_post)
        
        return {
            'endpoint': '/{page-id}/feed',
            'method': 'POST',
            'data': post_data
        }
    
    def _build_message(self, unified_post: UnifiedPost) -> str:
        """Build Facebook post message"""
        message_parts = []
        
        # Add title if present
        if unified_post.title:
            message_parts.append(unified_post.title)
        
        # Add body
        if unified_post.body:
            message_parts.append(unified_post.body)
        
        # Add hashtags
        if unified_post.tags:
            hashtags = unified_post.tags[:self.hashtag_limit]
            hashtag_text = ' '.join([f'#{tag}' for tag in hashtags])
            message_parts.append(hashtag_text)
        
        return '\n\n'.join(message_parts)
    
    def _create_album_post(self, unified_post: UnifiedPost, message: str) -> Dict[str, Any]:
        """Create Facebook album post for multiple media"""
        album_data = {
            'name': unified_post.title or 'Social Media Post',
            'message': message,
            'access_token': '{access_token}'
        }
        
        return {
            'endpoint': '/{page-id}/albums',
            'method': 'POST',
            'data': album_data,
            'requires_media_upload': True,
            'media_items': unified_post.media_items
        }

class LinkedInTransformer(BaseTransformer):
    """LinkedIn platform transformer"""
    
    def __init__(self):
        super().__init__(PlatformType.LINKEDIN)
        self.character_limit = 3000
        self.media_limit = 9
        self.hashtag_limit = 5  # Recommended
    
    def transform(self, unified_post: UnifiedPost) -> Dict[str, Any]:
        """Transform to LinkedIn API format"""
        content = unified_post.get_platform_content(self.platform)
        
        # Build post text
        post_text = self._build_post_text(unified_post)
        
        # Determine post type
        if unified_post.post_type == PostType.BLOG and unified_post.title:
            return self._create_article(unified_post)
        else:
            return self._create_share(unified_post, post_text)
    
    def _create_share(self, unified_post: UnifiedPost, text: str) -> Dict[str, Any]:
        """Create LinkedIn share (regular post)"""
        share_data = {
            'author': 'urn:li:person:{person-id}',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': text
                    },
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }
        
        # Add media if present
        if unified_post.media_items:
            media_item = unified_post.media_items[0]
            if media_item.get('media_type') == 'video':
                share_data['specificContent']['com.linkedin.ugc.ShareContent']['shareMediaCategory'] = 'VIDEO'
            else:
                share_data['specificContent']['com.linkedin.ugc.ShareContent']['shareMediaCategory'] = 'IMAGE'
            
            share_data['specificContent']['com.linkedin.ugc.ShareContent']['media'] = [
                {
                    'status': 'READY',
                    'description': {
                        'text': unified_post.summary or unified_post.body[:100]
                    },
                    'media': 'urn:li:digitalmediaAsset:{media-id}',
                    'title': {
                        'text': unified_post.title or 'Media'
                    }
                }
            ]
        
        return {
            'endpoint': '/v2/ugcPosts',
            'method': 'POST',
            'data': share_data,
            'requires_media_upload': len(unified_post.media_items) > 0
        }
    
    def _create_article(self, unified_post: UnifiedPost) -> Dict[str, Any]:
        """Create LinkedIn article"""
        article_data = {
            'author': 'urn:li:person:{person-id}',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': unified_post.summary or unified_post.body[:200]
                    },
                    'shareMediaCategory': 'ARTICLE',
                    'media': [
                        {
                            'status': 'READY',
                            'description': {
                                'text': unified_post.summary or unified_post.body[:100]
                            },
                            'originalUrl': unified_post.links[0] if unified_post.links else '',
                            'title': {
                                'text': unified_post.title
                            }
                        }
                    ]
                }
            }
        }
        
        return {
            'endpoint': '/v2/ugcPosts',
            'method': 'POST',
            'data': article_data
        }
    
    def _build_post_text(self, unified_post: UnifiedPost) -> str:
        """Build LinkedIn post text"""
        text_parts = []
        
        # Add title if present
        if unified_post.title:
            text_parts.append(unified_post.title)
        
        # Add body
        if unified_post.body:
            text_parts.append(unified_post.body)
        
        # Add links with UTM tracking
        if unified_post.links:
            text_parts.append("\n🔗 Read more:")
            for link in unified_post.links:
                tracked_link = self.add_utm_tracking(link, unified_post)
                text_parts.append(tracked_link)
        
        # Add hashtags (LinkedIn recommends 3-5)
        if unified_post.tags:
            hashtags = unified_post.tags[:self.hashtag_limit]
            hashtag_text = ' '.join([f'#{tag}' for tag in hashtags])
            text_parts.append(f"\n{hashtag_text}")
        
        full_text = '\n'.join(text_parts)
        
        # Truncate if necessary
        if len(full_text) > self.character_limit:
            full_text = full_text[:self.character_limit - 3] + '...'
        
        return full_text

class TransformerFactory:
    """Factory for creating platform-specific transformers"""
    
    _transformers = {
        PlatformType.TWITTER: TwitterTransformer,
        PlatformType.INSTAGRAM: InstagramTransformer,
        PlatformType.FACEBOOK: FacebookTransformer,
        PlatformType.LINKEDIN: LinkedInTransformer,
    }
    
    @classmethod
    def get_transformer(cls, platform: PlatformType) -> BaseTransformer:
        """Get transformer for specified platform"""
        transformer_class = cls._transformers.get(platform)
        if not transformer_class:
            raise ValueError(f"No transformer available for platform: {platform}")
        
        return transformer_class()
    
    @classmethod
    def transform_post(cls, unified_post: UnifiedPost, platform: PlatformType) -> Dict[str, Any]:
        """Transform unified post for specific platform"""
        transformer = cls.get_transformer(platform)
        return transformer.transform(unified_post)
    
    @classmethod
    def validate_post(cls, unified_post: UnifiedPost, platform: PlatformType) -> Tuple[bool, List[str]]:
        """Validate post for specific platform"""
        transformer = cls.get_transformer(platform)
        transformed_content = transformer.transform(unified_post)
        return transformer.validate_content(transformed_content.get('data', {}))

# Utility functions
def get_platform_limits(platform: PlatformType) -> Dict[str, int]:
    """Get platform-specific limits"""
    transformer = TransformerFactory.get_transformer(platform)
    return {
        'character_limit': transformer.character_limit,
        'media_limit': transformer.media_limit,
        'hashtag_limit': transformer.hashtag_limit,
        'mention_limit': transformer.mention_limit
    }

def preview_transformed_content(unified_post: UnifiedPost, platforms: List[PlatformType]) -> Dict[str, Any]:
    """Preview how content will look on different platforms"""
    previews = {}
    
    for platform in platforms:
        try:
            transformer = TransformerFactory.get_transformer(platform)
            transformed = transformer.transform(unified_post)
            is_valid, errors = transformer.validate_content(transformed.get('data', {}))
            
            previews[platform.value] = {
                'transformed_content': transformed,
                'is_valid': is_valid,
                'validation_errors': errors,
                'estimated_length': len(str(transformed.get('data', {}).get('text', ''))),
                'character_limit': transformer.character_limit
            }
        except Exception as e:
            logger.error(f"Error transforming content for {platform.value}: {str(e)}")
            previews[platform.value] = {
                'error': str(e),
                'is_valid': False
            }
    
    return previews

