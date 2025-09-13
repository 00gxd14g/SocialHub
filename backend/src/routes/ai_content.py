"""
AI Content routes for content generation and optimization
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.ai_content_service import ai_content_service
from ..models.user import User
import logging

ai_content_bp = Blueprint('ai_content', __name__)
logger = logging.getLogger(__name__)

@ai_content_bp.route('/generate-post', methods=['POST'])
@jwt_required()
def generate_post():
    """Generate AI-powered social media post content"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('topic'):
            return jsonify({'error': 'Topic is required'}), 400
        
        topic = data.get('topic')
        platform = data.get('platform', 'facebook')
        tone = data.get('tone', 'professional')
        length = data.get('length', 'medium')
        
        # Generate content using AI service
        result = ai_content_service.generate_post_content(
            topic=topic,
            platform=platform,
            tone=tone,
            length=length
        )
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to generate content')
            }), 400
            
    except Exception as e:
        logger.error(f"Error in generate_post: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@ai_content_bp.route('/generate-hashtags', methods=['POST'])
@jwt_required()
def generate_hashtags():
    """Generate relevant hashtags for content"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'error': 'Content is required'}), 400
        
        content = data.get('content')
        platform = data.get('platform', 'general')
        count = data.get('count', 10)
        
        # Validate count
        if count > 30:
            count = 30
        elif count < 1:
            count = 5
        
        result = ai_content_service.generate_hashtags(
            content=content,
            platform=platform,
            count=count
        )
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to generate hashtags')
            }), 400
            
    except Exception as e:
        logger.error(f"Error in generate_hashtags: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@ai_content_bp.route('/optimize-seo', methods=['POST'])
@jwt_required()
def optimize_seo():
    """Optimize content for SEO"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'error': 'Content is required'}), 400
        
        if not data.get('keywords'):
            return jsonify({'error': 'Target keywords are required'}), 400
        
        content = data.get('content')
        keywords = data.get('keywords')
        
        # Ensure keywords is a list
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(',')]
        
        result = ai_content_service.optimize_content_for_seo(
            content=content,
            target_keywords=keywords
        )
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to optimize content')
            }), 400
            
    except Exception as e:
        logger.error(f"Error in optimize_seo: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@ai_content_bp.route('/generate-variations', methods=['POST'])
@jwt_required()
def generate_variations():
    """Generate platform-specific content variations"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'error': 'Content is required'}), 400
        
        if not data.get('platforms'):
            return jsonify({'error': 'Target platforms are required'}), 400
        
        content = data.get('content')
        platforms = data.get('platforms')
        
        # Validate platforms
        valid_platforms = ['twitter', 'facebook', 'instagram', 'linkedin']
        platforms = [p for p in platforms if p in valid_platforms]
        
        if not platforms:
            return jsonify({'error': 'No valid platforms specified'}), 400
        
        result = ai_content_service.generate_content_variations(
            original_content=content,
            platforms=platforms
        )
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to generate variations')
            }), 400
            
    except Exception as e:
        logger.error(f"Error in generate_variations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@ai_content_bp.route('/analyze-sentiment', methods=['POST'])
@jwt_required()
def analyze_sentiment():
    """Analyze content sentiment and engagement potential"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'error': 'Content is required'}), 400
        
        content = data.get('content')
        
        result = ai_content_service.analyze_content_sentiment(content)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to analyze content')
            }), 400
            
    except Exception as e:
        logger.error(f"Error in analyze_sentiment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@ai_content_bp.route('/generate-blog', methods=['POST'])
@jwt_required()
def generate_blog():
    """Generate a complete blog post"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('topic'):
            return jsonify({'error': 'Topic is required'}), 400
        
        topic = data.get('topic')
        target_audience = data.get('target_audience', 'general audience')
        word_count = data.get('word_count', 800)
        
        # Validate word count
        if word_count > 3000:
            word_count = 3000
        elif word_count < 200:
            word_count = 200
        
        result = ai_content_service.generate_blog_post(
            topic=topic,
            target_audience=target_audience,
            word_count=word_count
        )
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to generate blog post')
            }), 400
            
    except Exception as e:
        logger.error(f"Error in generate_blog: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@ai_content_bp.route('/content-ideas', methods=['POST'])
@jwt_required()
def get_content_ideas():
    """Get AI-generated content ideas based on industry/niche"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        industry = data.get('industry', 'general')
        platform = data.get('platform', 'all')
        count = data.get('count', 10)
        
        # Mock content ideas - in production, this would use AI to generate ideas
        content_ideas = [
            {
                "title": "5 Tips for Better Social Media Engagement",
                "description": "Share actionable tips to help your audience improve their social media presence",
                "platforms": ["facebook", "linkedin", "twitter"],
                "content_type": "educational",
                "estimated_engagement": "high"
            },
            {
                "title": "Behind the Scenes: Our Daily Workflow",
                "description": "Give your audience a peek into how your team works",
                "platforms": ["instagram", "facebook"],
                "content_type": "behind-the-scenes",
                "estimated_engagement": "medium"
            },
            {
                "title": "Industry Trends to Watch in 2024",
                "description": "Share insights about upcoming trends in your industry",
                "platforms": ["linkedin", "twitter"],
                "content_type": "thought-leadership",
                "estimated_engagement": "high"
            },
            {
                "title": "Customer Success Story",
                "description": "Highlight how your product/service helped a customer",
                "platforms": ["all"],
                "content_type": "testimonial",
                "estimated_engagement": "medium"
            },
            {
                "title": "Quick Tutorial: Getting Started",
                "description": "Create a step-by-step guide for beginners",
                "platforms": ["youtube", "instagram", "tiktok"],
                "content_type": "tutorial",
                "estimated_engagement": "high"
            }
        ]
        
        # Filter by platform if specified
        if platform != 'all':
            filtered_ideas = []
            for idea in content_ideas:
                if platform in idea['platforms'] or 'all' in idea['platforms']:
                    filtered_ideas.append(idea)
            content_ideas = filtered_ideas
        
        # Limit to requested count
        content_ideas = content_ideas[:count]
        
        return jsonify({
            'success': True,
            'data': {
                'industry': industry,
                'platform': platform,
                'ideas': content_ideas,
                'total_count': len(content_ideas)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_content_ideas: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@ai_content_bp.route('/trending-topics', methods=['GET'])
@jwt_required()
def get_trending_topics():
    """Get trending topics for content creation"""
    try:
        user_id = get_jwt_identity()
        platform = request.args.get('platform', 'all')
        category = request.args.get('category', 'general')
        
        # Mock trending topics - in production, this would fetch real trending data
        trending_topics = [
            {
                "topic": "Artificial Intelligence",
                "trend_score": 95,
                "platforms": ["linkedin", "twitter"],
                "hashtags": ["#AI", "#ArtificialIntelligence", "#MachineLearning"],
                "volume": "125K mentions"
            },
            {
                "topic": "Remote Work",
                "trend_score": 87,
                "platforms": ["linkedin", "facebook"],
                "hashtags": ["#RemoteWork", "#WorkFromHome", "#DigitalNomad"],
                "volume": "89K mentions"
            },
            {
                "topic": "Sustainability",
                "trend_score": 82,
                "platforms": ["instagram", "facebook"],
                "hashtags": ["#Sustainability", "#EcoFriendly", "#GreenLiving"],
                "volume": "67K mentions"
            },
            {
                "topic": "Social Media Marketing",
                "trend_score": 78,
                "platforms": ["all"],
                "hashtags": ["#SocialMediaMarketing", "#DigitalMarketing", "#ContentCreation"],
                "volume": "54K mentions"
            },
            {
                "topic": "Cryptocurrency",
                "trend_score": 75,
                "platforms": ["twitter", "reddit"],
                "hashtags": ["#Crypto", "#Bitcoin", "#Blockchain"],
                "volume": "43K mentions"
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'platform': platform,
                'category': category,
                'trending_topics': trending_topics,
                'last_updated': '2024-01-15T10:00:00Z'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_trending_topics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

