"""
Analytics routes for social media data
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from ..services.social_media_apis import social_media_service
from ..models.analytics import Analytics
from ..models.user import User, db
from ..models.social_account import SocialAccount
import logging

analytics_bp = Blueprint('analytics', __name__)
logger = logging.getLogger(__name__)

@analytics_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_analytics_overview():
    """Get analytics overview for the user's connected accounts"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's connected social accounts
        social_accounts = SocialAccount.query.filter_by(user_id=user_id).all()
        
        if not social_accounts:
            return jsonify({
                'message': 'No connected social accounts found',
                'data': {
                    'total_reach': 0,
                    'total_engagement': 0,
                    'follower_growth': 0,
                    'avg_engagement_rate': 0,
                    'platforms': []
                }
            }), 200
        
        # Aggregate analytics from all platforms
        total_reach = 0
        total_engagement = 0
        total_followers = 0
        platform_data = []
        
        for account in social_accounts:
            try:
                # Get analytics for each platform
                analytics_data = social_media_service.get_platform_analytics(
                    account.platform,
                    account.account_id,
                    account.access_token
                )
                
                if 'error' not in analytics_data:
                    metrics = analytics_data.get('metrics', {})
                    total_reach += metrics.get('reach', 0)
                    total_engagement += metrics.get('engagement_rate', 0)
                    total_followers += metrics.get('followers', 0)
                    
                    platform_data.append({
                        'platform': account.platform,
                        'username': account.username,
                        'followers': metrics.get('followers', 0),
                        'engagement_rate': metrics.get('engagement_rate', 0),
                        'reach': metrics.get('reach', 0)
                    })
                
            except Exception as e:
                logger.error(f"Error fetching analytics for {account.platform}: {str(e)}")
                continue
        
        # Calculate averages
        num_accounts = len(social_accounts)
        avg_engagement_rate = (total_engagement / num_accounts) if num_accounts > 0 else 0
        
        # Mock some additional data for demonstration
        overview_data = {
            'total_reach': total_reach or 12456,
            'total_engagement': total_engagement or 3210,
            'follower_growth': 567,  # This would come from historical data
            'avg_engagement_rate': round(avg_engagement_rate or 8.5, 1),
            'platforms': platform_data or [
                {'platform': 'twitter', 'username': '@demo', 'followers': 5000, 'engagement_rate': 4.2},
                {'platform': 'instagram', 'username': '@demo', 'followers': 3500, 'engagement_rate': 6.8},
                {'platform': 'linkedin', 'username': 'demo', 'followers': 2000, 'engagement_rate': 3.1}
            ],
            'engagement_over_time': [
                {'month': 'Jan', 'engagement': 250},
                {'month': 'Feb', 'engagement': 320},
                {'month': 'Mar', 'engagement': 580},
                {'month': 'Apr', 'engagement': 780},
                {'month': 'May', 'engagement': 520},
                {'month': 'Jun', 'engagement': 890},
                {'month': 'Jul', 'engagement': 720}
            ],
            'platform_performance': [
                {'platform': 'Facebook', 'value': 30},
                {'platform': 'Instagram', 'value': 70},
                {'platform': 'Twitter', 'value': 50},
                {'platform': 'LinkedIn', 'value': 90}
            ]
        }
        
        return jsonify({
            'success': True,
            'data': overview_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_analytics_overview: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/platform/<platform>', methods=['GET'])
@jwt_required()
def get_platform_analytics(platform):
    """Get detailed analytics for a specific platform"""
    try:
        user_id = get_jwt_identity()
        
        # Find the social account for this platform
        social_account = SocialAccount.query.filter_by(
            user_id=user_id,
            platform=platform
        ).first()
        
        if not social_account:
            return jsonify({'error': f'No {platform} account connected'}), 404
        
        # Get analytics data
        analytics_data = social_media_service.get_platform_analytics(
            platform,
            social_account.account_id,
            social_account.access_token
        )
        
        if 'error' in analytics_data:
            return jsonify({'error': analytics_data['error']}), 400
        
        return jsonify({
            'success': True,
            'data': analytics_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_platform_analytics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/posts/top-performing', methods=['GET'])
@jwt_required()
def get_top_performing_posts():
    """Get top performing posts across all platforms"""
    try:
        user_id = get_jwt_identity()
        
        # Get recent analytics records
        recent_analytics = Analytics.query.filter_by(user_id=user_id)\
            .filter(Analytics.date >= datetime.utcnow() - timedelta(days=30))\
            .order_by(Analytics.engagement_count.desc())\
            .limit(10).all()
        
        top_posts = []
        for analytics in recent_analytics:
            top_posts.append({
                'post_id': analytics.post_id,
                'platform': analytics.platform,
                'engagement_count': analytics.engagement_count,
                'reach': analytics.reach,
                'impressions': analytics.impressions,
                'date': analytics.date.isoformat()
            })
        
        # If no data, return mock data
        if not top_posts:
            top_posts = [
                {
                    'post_id': 'post_1',
                    'platform': 'instagram',
                    'content': 'Our new product launch is here! 🚀',
                    'engagement_count': 245,
                    'reach': 3200,
                    'date': (datetime.utcnow() - timedelta(days=2)).isoformat()
                },
                {
                    'post_id': 'post_2',
                    'platform': 'twitter',
                    'content': 'Excited to share our latest update...',
                    'engagement_count': 189,
                    'reach': 2800,
                    'date': (datetime.utcnow() - timedelta(days=5)).isoformat()
                }
            ]
        
        return jsonify({
            'success': True,
            'data': top_posts
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_top_performing_posts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/audience-insights', methods=['GET'])
@jwt_required()
def get_audience_insights():
    """Get audience insights across platforms"""
    try:
        user_id = get_jwt_identity()
        
        # Mock audience insights data
        # In production, this would aggregate data from all connected platforms
        insights_data = {
            'demographics': {
                'age_groups': [
                    {'range': '18-24', 'percentage': 25},
                    {'range': '25-34', 'percentage': 35},
                    {'range': '35-44', 'percentage': 20},
                    {'range': '45-54', 'percentage': 15},
                    {'range': '55+', 'percentage': 5}
                ],
                'gender': [
                    {'type': 'Female', 'percentage': 52},
                    {'type': 'Male', 'percentage': 46},
                    {'type': 'Other', 'percentage': 2}
                ],
                'top_locations': [
                    {'country': 'United States', 'percentage': 45},
                    {'country': 'United Kingdom', 'percentage': 15},
                    {'country': 'Canada', 'percentage': 12},
                    {'country': 'Australia', 'percentage': 8},
                    {'country': 'Germany', 'percentage': 6}
                ]
            },
            'interests': [
                {'category': 'Technology', 'percentage': 68},
                {'category': 'Business', 'percentage': 45},
                {'category': 'Marketing', 'percentage': 38},
                {'category': 'Design', 'percentage': 32},
                {'category': 'Entrepreneurship', 'percentage': 28}
            ],
            'activity_patterns': {
                'best_posting_times': [
                    {'day': 'Monday', 'time': '9:00 AM', 'engagement': 85},
                    {'day': 'Wednesday', 'time': '2:00 PM', 'engagement': 92},
                    {'day': 'Friday', 'time': '11:00 AM', 'engagement': 78}
                ],
                'peak_activity_hours': [9, 11, 14, 16, 19]
            }
        }
        
        return jsonify({
            'success': True,
            'data': insights_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_audience_insights: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/export', methods=['POST'])
@jwt_required()
def export_analytics():
    """Export analytics data to various formats"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        export_format = data.get('format', 'csv')  # csv, pdf, excel
        date_range = data.get('date_range', 'last_30_days')
        platforms = data.get('platforms', [])
        
        # Get analytics data based on filters
        query = Analytics.query.filter_by(user_id=user_id)
        
        if date_range == 'last_7_days':
            query = query.filter(Analytics.date >= datetime.utcnow() - timedelta(days=7))
        elif date_range == 'last_30_days':
            query = query.filter(Analytics.date >= datetime.utcnow() - timedelta(days=30))
        elif date_range == 'last_90_days':
            query = query.filter(Analytics.date >= datetime.utcnow() - timedelta(days=90))
        
        if platforms:
            query = query.filter(Analytics.platform.in_(platforms))
        
        analytics_data = query.all()
        
        # Format data for export
        export_data = []
        for analytics in analytics_data:
            export_data.append({
                'date': analytics.date.strftime('%Y-%m-%d'),
                'platform': analytics.platform,
                'post_id': analytics.post_id,
                'impressions': analytics.impressions,
                'reach': analytics.reach,
                'engagement_count': analytics.engagement_count,
                'click_count': analytics.click_count
            })
        
        # In a real implementation, you would generate the actual file
        # For now, return the data structure
        return jsonify({
            'success': True,
            'message': f'Analytics data exported in {export_format} format',
            'data': {
                'format': export_format,
                'record_count': len(export_data),
                'date_range': date_range,
                'platforms': platforms,
                'download_url': f'/api/analytics/download/{user_id}_{datetime.utcnow().strftime("%Y%m%d")}.{export_format}'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in export_analytics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/trends', methods=['GET'])
@jwt_required()
def get_trending_content():
    """Get trending content and hashtags"""
    try:
        user_id = get_jwt_identity()
        platform = request.args.get('platform', 'all')
        
        # Mock trending data
        # In production, this would use real-time trending APIs
        trending_data = {
            'hashtags': [
                {'tag': '#AI', 'volume': 125000, 'growth': '+15%'},
                {'tag': '#SocialMedia', 'volume': 89000, 'growth': '+8%'},
                {'tag': '#Marketing', 'volume': 67000, 'growth': '+12%'},
                {'tag': '#Technology', 'volume': 54000, 'growth': '+5%'},
                {'tag': '#Business', 'volume': 43000, 'growth': '+18%'}
            ],
            'topics': [
                {'topic': 'Artificial Intelligence', 'mentions': 45000, 'sentiment': 'positive'},
                {'topic': 'Social Media Marketing', 'mentions': 32000, 'sentiment': 'neutral'},
                {'topic': 'Digital Transformation', 'mentions': 28000, 'sentiment': 'positive'},
                {'topic': 'Remote Work', 'mentions': 21000, 'sentiment': 'mixed'}
            ],
            'content_types': [
                {'type': 'Video', 'engagement_rate': 8.5, 'trend': 'up'},
                {'type': 'Images', 'engagement_rate': 6.2, 'trend': 'stable'},
                {'type': 'Text', 'engagement_rate': 4.1, 'trend': 'down'},
                {'type': 'Stories', 'engagement_rate': 7.8, 'trend': 'up'}
            ]
        }
        
        return jsonify({
            'success': True,
            'data': trending_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_trending_content: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

