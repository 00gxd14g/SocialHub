from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from src.models.user import db

class Analytics(db.Model):
    __tablename__ = 'analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    social_account_id = db.Column(db.Integer, db.ForeignKey('social_accounts.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    posts_count = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float, default=0.0)
    reach = db.Column(db.Integer, default=0)
    impressions = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    profile_visits = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    social_account = db.relationship('SocialAccount', backref=db.backref('analytics', lazy=True))
    
    def __repr__(self):
        return f'<Analytics {self.social_account_id}:{self.date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'social_account_id': self.social_account_id,
            'date': self.date.isoformat() if self.date else None,
            'followers_count': self.followers_count,
            'following_count': self.following_count,
            'posts_count': self.posts_count,
            'engagement_rate': self.engagement_rate,
            'reach': self.reach,
            'impressions': self.impressions,
            'likes': self.likes,
            'comments': self.comments,
            'shares': self.shares,
            'profile_visits': self.profile_visits,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

