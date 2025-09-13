"""
Unified Post Model for Cross-Platform Social Media Management
Implements single-schema orchestration for all social media platforms
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
import enum
import uuid
import json
from typing import List, Dict, Optional, Any

from .user import db

class PostStatus(enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    QUEUED = "queued"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PostType(enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    BLOG = "blog"

class PlatformType(enum.Enum):
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    MEDIUM = "medium"
    WORDPRESS = "wordpress"

class UnifiedPost(db.Model):
    """
    Unified post model that serves as the single source of truth
    for all social media content across platforms
    """
    __tablename__ = 'unified_posts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Unified Content Schema
    title = Column(String(500))  # For blog posts, LinkedIn articles
    body = Column(Text, nullable=False)  # Main content/caption
    summary = Column(Text)  # Short description for previews
    
    # Media and Assets
    media_items = Column(JSON, default=list)  # List of media objects
    thumbnail_url = Column(String(500))  # Thumbnail for videos
    
    # Metadata
    tags = Column(JSON, default=list)  # Hashtags without #
    mentions = Column(JSON, default=list)  # @mentions
    links = Column(JSON, default=list)  # External links
    location = Column(JSON)  # Geographic location data
    
    # Content Classification
    post_type = Column(Enum(PostType), default=PostType.TEXT)
    category = Column(String(100))  # Content category
    language = Column(String(10), default='en')
    
    # Scheduling and Publishing
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    scheduled_time = Column(DateTime)
    published_at = Column(DateTime)
    expires_at = Column(DateTime)  # For stories, temporary content
    
    # Platform Configuration
    target_platforms = Column(JSON, default=list)  # List of platforms to publish to
    platform_configs = Column(JSON, default=dict)  # Platform-specific configurations
    
    # SEO and Analytics
    seo_title = Column(String(200))
    seo_description = Column(String(500))
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_campaign = Column(String(100))
    utm_content = Column(String(100))
    
    # Orchestration
    idempotency_key = Column(String(100), unique=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_error = Column(Text)
    
    # Thread/Series Support
    is_thread = Column(Boolean, default=False)
    thread_parent_id = Column(Integer, ForeignKey('unified_posts.id'))
    thread_order = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="unified_posts")
    platform_posts = relationship("PlatformPost", back_populates="unified_post", cascade="all, delete-orphan")
    thread_children = relationship("UnifiedPost", backref="thread_parent", remote_side=[id])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.idempotency_key:
            self.idempotency_key = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'body': self.body,
            'summary': self.summary,
            'media_items': self.media_items,
            'thumbnail_url': self.thumbnail_url,
            'tags': self.tags,
            'mentions': self.mentions,
            'links': self.links,
            'location': self.location,
            'post_type': self.post_type.value if self.post_type else None,
            'category': self.category,
            'language': self.language,
            'status': self.status.value if self.status else None,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'target_platforms': self.target_platforms,
            'platform_configs': self.platform_configs,
            'seo_title': self.seo_title,
            'seo_description': self.seo_description,
            'utm_params': {
                'source': self.utm_source,
                'medium': self.utm_medium,
                'campaign': self.utm_campaign,
                'content': self.utm_content
            },
            'is_thread': self.is_thread,
            'thread_parent_id': self.thread_parent_id,
            'thread_order': self.thread_order,
            'retry_count': self.retry_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_platform_content(self, platform: PlatformType) -> Dict[str, Any]:
        """Get platform-specific content configuration"""
        platform_key = platform.value
        config = self.platform_configs.get(platform_key, {})
        
        # Base content
        content = {
            'title': self.title,
            'body': self.body,
            'media_items': self.media_items,
            'tags': self.tags,
            'mentions': self.mentions,
            'links': self.links,
            'location': self.location
        }
        
        # Apply platform-specific overrides
        if config:
            content.update(config)
        
        return content
    
    def add_utm_params(self, url: str, platform: str) -> str:
        """Add UTM parameters to URLs for tracking"""
        if not url or '?' in url:
            return url
        
        utm_params = []
        if self.utm_source:
            utm_params.append(f"utm_source={self.utm_source}")
        if self.utm_medium:
            utm_params.append(f"utm_medium={self.utm_medium}")
        if self.utm_campaign:
            utm_params.append(f"utm_campaign={self.utm_campaign}")
        if self.utm_content:
            utm_params.append(f"utm_content={self.utm_content}")
        
        # Add platform-specific UTM
        utm_params.append(f"utm_platform={platform}")
        
        if utm_params:
            return f"{url}?{'&'.join(utm_params)}"
        return url

class PlatformPost(db.Model):
    """
    Platform-specific post instances created from unified posts
    Tracks the status and metadata for each platform
    """
    __tablename__ = 'platform_posts'
    
    id = Column(Integer, primary_key=True)
    unified_post_id = Column(Integer, ForeignKey('unified_posts.id'), nullable=False)
    platform = Column(Enum(PlatformType), nullable=False)
    
    # Platform-specific identifiers
    platform_post_id = Column(String(255))  # ID from the platform
    platform_url = Column(String(500))  # Direct URL to the post
    
    # Publishing status
    status = Column(Enum(PostStatus), default=PostStatus.QUEUED)
    scheduled_time = Column(DateTime)
    published_at = Column(DateTime)
    
    # Platform-specific content (transformed)
    transformed_content = Column(JSON)  # Platform-adapted content
    media_ids = Column(JSON, default=list)  # Platform media IDs
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    last_attempt_at = Column(DateTime)
    next_retry_at = Column(DateTime)
    
    # Analytics tracking
    analytics_data = Column(JSON, default=dict)
    last_analytics_update = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    unified_post = relationship("UnifiedPost", back_populates="platform_posts")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'unified_post_id': self.unified_post_id,
            'platform': self.platform.value if self.platform else None,
            'platform_post_id': self.platform_post_id,
            'platform_url': self.platform_url,
            'status': self.status.value if self.status else None,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'transformed_content': self.transformed_content,
            'media_ids': self.media_ids,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'analytics_data': self.analytics_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MediaItem(db.Model):
    """
    Media items associated with posts
    Supports multiple formats and platform-specific processing
    """
    __tablename__ = 'media_items'
    
    id = Column(Integer, primary_key=True)
    unified_post_id = Column(Integer, ForeignKey('unified_posts.id'), nullable=False)
    
    # Media metadata
    original_url = Column(String(500), nullable=False)
    media_type = Column(String(50), nullable=False)  # image, video, gif, document
    file_size = Column(Integer)  # in bytes
    duration = Column(Integer)  # for videos, in seconds
    width = Column(Integer)
    height = Column(Integer)
    
    # Processing status
    processing_status = Column(String(50), default='pending')  # pending, processing, ready, failed
    processed_urls = Column(JSON, default=dict)  # Platform-specific processed URLs
    
    # Platform-specific media IDs
    platform_media_ids = Column(JSON, default=dict)  # {platform: media_id}
    
    # Metadata
    alt_text = Column(Text)  # Accessibility
    caption = Column(Text)  # Media-specific caption
    tags = Column(JSON, default=list)  # People tags for photos
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'original_url': self.original_url,
            'media_type': self.media_type,
            'file_size': self.file_size,
            'duration': self.duration,
            'width': self.width,
            'height': self.height,
            'processing_status': self.processing_status,
            'processed_urls': self.processed_urls,
            'platform_media_ids': self.platform_media_ids,
            'alt_text': self.alt_text,
            'caption': self.caption,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EventStore(db.Model):
    """
    Unified event store for all platform activities
    Normalizes webhooks and polling data
    """
    __tablename__ = 'event_store'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    unified_post_id = Column(Integer, ForeignKey('unified_posts.id'))
    platform_post_id = Column(Integer, ForeignKey('platform_posts.id'))
    
    # Event metadata
    event_type = Column(String(100), nullable=False)  # like, comment, share, mention, etc.
    platform = Column(Enum(PlatformType), nullable=False)
    platform_event_id = Column(String(255))  # Platform's event ID
    
    # Event data
    event_data = Column(JSON, nullable=False)  # Raw event data
    normalized_data = Column(JSON)  # Normalized event data
    
    # Actor information
    actor_id = Column(String(255))  # Platform user ID who triggered event
    actor_username = Column(String(255))
    actor_display_name = Column(String(255))
    
    # Timestamps
    event_timestamp = Column(DateTime, nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_error = Column(Text)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'unified_post_id': self.unified_post_id,
            'platform_post_id': self.platform_post_id,
            'event_type': self.event_type,
            'platform': self.platform.value if self.platform else None,
            'platform_event_id': self.platform_event_id,
            'event_data': self.event_data,
            'normalized_data': self.normalized_data,
            'actor_id': self.actor_id,
            'actor_username': self.actor_username,
            'actor_display_name': self.actor_display_name,
            'event_timestamp': self.event_timestamp.isoformat() if self.event_timestamp else None,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'is_processed': self.is_processed
        }

# Add relationship to User model
from .user import User
User.unified_posts = relationship("UnifiedPost", back_populates="user", cascade="all, delete-orphan")

