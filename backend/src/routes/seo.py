"""
SEO routes for content optimization and analysis
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.seo_service import seo_service
from ..models.user import User
import logging

seo_bp = Blueprint('seo', __name__)
logger = logging.getLogger(__name__)

@seo_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_content():
    """Analyze content for SEO factors"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'error': 'Content is required'}), 400
        
        content = data.get('content')
        target_keywords = data.get('target_keywords', [])
        
        # Ensure target_keywords is a list
        if isinstance(target_keywords, str):
            target_keywords = [kw.strip() for kw in target_keywords.split(',') if kw.strip()]
        
        result = seo_service.analyze_content_seo(content, target_keywords)
        
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
        logger.error(f"Error in analyze_content: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@seo_bp.route('/meta-tags', methods=['POST'])
@jwt_required()
def generate_meta_tags():
    """Generate SEO meta tags for content"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'error': 'Content is required'}), 400
        
        content = data.get('content')
        title = data.get('title')
        
        result = seo_service.generate_meta_tags(content, title)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to generate meta tags')
            }), 400
            
    except Exception as e:
        logger.error(f"Error in generate_meta_tags: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@seo_bp.route('/optimize', methods=['POST'])
@jwt_required()
def optimize_content():
    """Optimize content for specific keywords"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'error': 'Content is required'}), 400
        
        if not data.get('target_keywords'):
            return jsonify({'error': 'Target keywords are required'}), 400
        
        content = data.get('content')
        target_keywords = data.get('target_keywords')
        
        # Ensure target_keywords is a list
        if isinstance(target_keywords, str):
            target_keywords = [kw.strip() for kw in target_keywords.split(',') if kw.strip()]
        
        if not target_keywords:
            return jsonify({'error': 'At least one target keyword is required'}), 400
        
        result = seo_service.optimize_content_for_keywords(content, target_keywords)
        
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
        logger.error(f"Error in optimize_content: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@seo_bp.route('/schema-markup', methods=['POST'])
@jwt_required()
def generate_schema_markup():
    """Generate JSON-LD schema markup"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('content_type'):
            return jsonify({'error': 'Content type is required'}), 400
        
        content_type = data.get('content_type')
        schema_data = data.get('data', {})
        
        # Validate content type
        valid_types = ['article', 'organization', 'website']
        if content_type not in valid_types:
            return jsonify({
                'error': f'Invalid content type. Must be one of: {", ".join(valid_types)}'
            }), 400
        
        result = seo_service.generate_schema_markup(content_type, schema_data)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to generate schema markup')
            }), 400
            
    except Exception as e:
        logger.error(f"Error in generate_schema_markup: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@seo_bp.route('/competitor-analysis', methods=['POST'])
@jwt_required()
def analyze_competitors():
    """Analyze competitor content for SEO insights"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('competitor_urls'):
            return jsonify({'error': 'Competitor URLs are required'}), 400
        
        competitor_urls = data.get('competitor_urls')
        target_keywords = data.get('target_keywords', [])
        
        # Validate URLs
        if not isinstance(competitor_urls, list) or len(competitor_urls) == 0:
            return jsonify({'error': 'At least one competitor URL is required'}), 400
        
        # Limit to 5 competitors for performance
        competitor_urls = competitor_urls[:5]
        
        # Ensure target_keywords is a list
        if isinstance(target_keywords, str):
            target_keywords = [kw.strip() for kw in target_keywords.split(',') if kw.strip()]
        
        result = seo_service.analyze_competitor_content(competitor_urls, target_keywords)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to analyze competitors')
            }), 400
            
    except Exception as e:
        logger.error(f"Error in analyze_competitors: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@seo_bp.route('/keyword-suggestions', methods=['POST'])
@jwt_required()
def get_keyword_suggestions():
    """Get keyword suggestions for content"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        topic = data.get('topic', '')
        industry = data.get('industry', 'general')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Mock keyword suggestions - in production, this would use keyword research APIs
        keyword_suggestions = {
            'primary_keywords': [
                {'keyword': f'{topic}', 'volume': 12000, 'difficulty': 'medium'},
                {'keyword': f'{topic} guide', 'volume': 8500, 'difficulty': 'low'},
                {'keyword': f'best {topic}', 'volume': 6200, 'difficulty': 'high'},
                {'keyword': f'{topic} tips', 'volume': 4800, 'difficulty': 'low'},
                {'keyword': f'how to {topic}', 'volume': 3900, 'difficulty': 'medium'}
            ],
            'long_tail_keywords': [
                {'keyword': f'{topic} for beginners', 'volume': 2100, 'difficulty': 'low'},
                {'keyword': f'{topic} best practices', 'volume': 1800, 'difficulty': 'medium'},
                {'keyword': f'{topic} strategy 2024', 'volume': 1500, 'difficulty': 'medium'},
                {'keyword': f'complete {topic} guide', 'volume': 1200, 'difficulty': 'low'},
                {'keyword': f'{topic} tools and techniques', 'volume': 950, 'difficulty': 'low'}
            ],
            'related_keywords': [
                {'keyword': f'{topic} automation', 'volume': 3200, 'difficulty': 'medium'},
                {'keyword': f'{topic} analytics', 'volume': 2800, 'difficulty': 'medium'},
                {'keyword': f'{topic} optimization', 'volume': 2400, 'difficulty': 'high'},
                {'keyword': f'{topic} management', 'volume': 2100, 'difficulty': 'medium'},
                {'keyword': f'{topic} platform', 'volume': 1900, 'difficulty': 'high'}
            ],
            'trending_keywords': [
                {'keyword': f'AI {topic}', 'volume': 5500, 'difficulty': 'high', 'trend': '+25%'},
                {'keyword': f'{topic} automation', 'volume': 3200, 'difficulty': 'medium', 'trend': '+18%'},
                {'keyword': f'{topic} ROI', 'volume': 2600, 'difficulty': 'medium', 'trend': '+12%'}
            ]
        }
        
        return jsonify({
            'success': True,
            'data': {
                'topic': topic,
                'industry': industry,
                'suggestions': keyword_suggestions,
                'total_keywords': sum(len(keywords) for keywords in keyword_suggestions.values())
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_keyword_suggestions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@seo_bp.route('/content-audit', methods=['POST'])
@jwt_required()
def audit_content():
    """Perform comprehensive SEO audit on content"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'error': 'Content is required'}), 400
        
        content = data.get('content')
        title = data.get('title', '')
        target_keywords = data.get('target_keywords', [])
        
        # Ensure target_keywords is a list
        if isinstance(target_keywords, str):
            target_keywords = [kw.strip() for kw in target_keywords.split(',') if kw.strip()]
        
        # Perform comprehensive analysis
        seo_analysis = seo_service.analyze_content_seo(content, target_keywords)
        meta_tags = seo_service.generate_meta_tags(content, title)
        
        # Compile audit results
        audit_results = {
            'content_analysis': seo_analysis,
            'meta_tags': meta_tags,
            'audit_summary': {
                'overall_score': seo_analysis.get('seo_score', {}).get('percentage', 0),
                'critical_issues': [],
                'warnings': [],
                'recommendations': seo_analysis.get('recommendations', [])
            }
        }
        
        # Identify critical issues and warnings
        if seo_analysis.get('success'):
            score = seo_analysis['seo_score']['percentage']
            metrics = seo_analysis['metrics']
            
            if score < 50:
                audit_results['audit_summary']['critical_issues'].append('Overall SEO score is critically low')
            
            if metrics['word_count'] < 300:
                audit_results['audit_summary']['critical_issues'].append('Content is too short for good SEO')
            
            if metrics['readability_score'] < 30:
                audit_results['audit_summary']['warnings'].append('Content readability needs improvement')
            
            if not target_keywords:
                audit_results['audit_summary']['warnings'].append('No target keywords specified')
        
        return jsonify({
            'success': True,
            'data': audit_results
        }), 200
        
    except Exception as e:
        logger.error(f"Error in audit_content: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

