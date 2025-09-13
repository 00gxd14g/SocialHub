from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    media_urls = db.Column(db.Text)  # JSON string of media URLs
    hashtags = db.Column(db.Text)  # JSON string of hashtags
    scheduled_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, published, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    
    def __repr__(self):
        return f'<Post {self.id}:{self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'media_urls': self.media_urls,
            'hashtags': self.hashtags,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PostPlatform(db.Model):
    __tablename__ = 'post_platforms'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    social_account_id = db.Column(db.Integer, db.ForeignKey('social_accounts.id'), nullable=False)
    platform_post_id = db.Column(db.String(100))  # ID from the social platform
    post_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')  # pending, published, failed
    error_message = db.Column(db.Text)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    post = db.relationship('Post', backref=db.backref('post_platforms', lazy=True))
    social_account = db.relationship('SocialAccount', backref=db.backref('post_platforms', lazy=True))
    
    def __repr__(self):
        return f'<PostPlatform {self.post_id}:{self.social_account_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'social_account_id': self.social_account_id,
            'platform_post_id': self.platform_post_id,
            'post_url': self.post_url,
            'status': self.status,
            'error_message': self.error_message,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

