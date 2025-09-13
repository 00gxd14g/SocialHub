"""
Unified Posts API Routes
Handles the unified post model with cross-platform orchestration
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import logging

from ..models.unified_post import UnifiedPost, PlatformPost, PostStatus, PostType, PlatformType
from ..models.user import db
from ..services.platform_transformers import TransformerFactory, preview_transformed_content
from ..services.queue_manager import queue_manager, create_post_job, JobPriority
from ..services.mcp_tools import mcp_registry

logger = logging.getLogger(__name__)

unified_posts_bp = Blueprint('unified_posts', __name__)

@unified_posts_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_unified_post():
    """Create a new unified post"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('body'):
            return jsonify({'error': 'Post body is required'}), 400
        
        if not data.get('target_platforms'):
            return jsonify({'error': 'At least one target platform is required'}), 400
        
        # Validate platforms
        valid_platforms = []
        for platform_name in data['target_platforms']:
            try:
                platform = PlatformType(platform_name.lower())
                valid_platforms.append(platform.value)
            except ValueError:
                return jsonify({'error': f'Invalid platform: {platform_name}'}), 400
        
        # Parse scheduled time if provided
        scheduled_time = None
        if data.get('scheduled_time'):
            try:
                scheduled_time = datetime.fromisoformat(data['scheduled_time'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid scheduled_time format. Use ISO format.'}), 400
        
        # Determine post type
        post_type = PostType.TEXT
        if data.get('post_type'):
            try:
                post_type = PostType(data['post_type'].lower())
            except ValueError:
                return jsonify({'error': f'Invalid post_type: {data["post_type"]}'}), 400
        
        # Create unified post
        unified_post = UnifiedPost(
            user_id=user_id,
            title=data.get('title'),
            body=data['body'],
            summary=data.get('summary'),
            media_items=data.get('media_items', []),
            tags=data.get('tags', []),
            mentions=data.get('mentions', []),
            links=data.get('links', []),
            location=data.get('location'),
            post_type=post_type,
            category=data.get('category'),
            language=data.get('language', 'en'),
            target_platforms=valid_platforms,
            platform_configs=data.get('platform_configs', {}),
            scheduled_time=scheduled_time,
            status=PostStatus.SCHEDULED if scheduled_time else PostStatus.DRAFT,
            seo_title=data.get('seo_title'),
            seo_description=data.get('seo_description'),
            utm_source=data.get('utm_source'),
            utm_medium=data.get('utm_medium'),
            utm_campaign=data.get('utm_campaign'),
            utm_content=data.get('utm_content'),
            is_thread=data.get('is_thread', False),
            thread_parent_id=data.get('thread_parent_id'),
            thread_order=data.get('thread_order', 1)
        )
        
        db.session.add(unified_post)
        db.session.commit()
        
        # Generate platform previews
        platform_enums = [PlatformType(p) for p in valid_platforms]
        previews = preview_transformed_content(unified_post, platform_enums)
        
        # Create platform posts
        platform_posts = []
        for platform_name in valid_platforms:
            platform_post = PlatformPost(
                unified_post_id=unified_post.id,
                platform=PlatformType(platform_name),
                status=PostStatus.QUEUED if scheduled_time else PostStatus.DRAFT,
                scheduled_time=scheduled_time
            )
            db.session.add(platform_post)
            platform_posts.append(platform_post)
        
        db.session.commit()
        
        # If scheduled, create queue jobs
        job_ids = []
        if scheduled_time:
            for platform_name in valid_platforms:
                job = create_post_job(
                    unified_post.id,
                    platform_name,
                    user_id,
                    scheduled_time
                )
                job_id = queue_manager.enqueue(job)
                job_ids.append(job_id)
        
        response_data = unified_post.to_dict()
        response_data['platform_posts'] = [pp.to_dict() for pp in platform_posts]
        response_data['previews'] = previews
        response_data['job_ids'] = job_ids
        
        return jsonify({
            'message': 'Unified post created successfully',
            'post': response_data
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating unified post: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@unified_posts_bp.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_unified_post(post_id):
    """Get a unified post by ID"""
    try:
        user_id = get_jwt_identity()
        
        unified_post = UnifiedPost.query.filter_by(
            id=post_id,
            user_id=user_id
        ).first()
        
        if not unified_post:
            return jsonify({'error': 'Post not found'}), 404
        
        response_data = unified_post.to_dict()
        response_data['platform_posts'] = [pp.to_dict() for pp in unified_post.platform_posts]
        
        return jsonify({'post': response_data})
        
    except Exception as e:
        logger.error(f"Error getting unified post: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@unified_posts_bp.route('/posts', methods=['GET'])
@jwt_required()
def list_unified_posts():
    """List user's unified posts with pagination"""
    try:
        user_id = get_jwt_identity()
        
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Filter parameters
        status = request.args.get('status')
        post_type = request.args.get('post_type')
        platform = request.args.get('platform')
        
        # Build query
        query = UnifiedPost.query.filter_by(user_id=user_id)
        
        if status:
            try:
                status_enum = PostStatus(status.lower())
                query = query.filter_by(status=status_enum)
            except ValueError:
                return jsonify({'error': f'Invalid status: {status}'}), 400
        
        if post_type:
            try:
                type_enum = PostType(post_type.lower())
                query = query.filter_by(post_type=type_enum)
            except ValueError:
                return jsonify({'error': f'Invalid post_type: {post_type}'}), 400
        
        if platform:
            query = query.filter(UnifiedPost.target_platforms.contains([platform]))
        
        # Order by creation date (newest first)
        query = query.order_by(UnifiedPost.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        posts = []
        for post in pagination.items:
            post_data = post.to_dict()
            post_data['platform_posts'] = [pp.to_dict() for pp in post.platform_posts]
            posts.append(post_data)
        
        return jsonify({
            'posts': posts,
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Error listing unified posts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@unified_posts_bp.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_unified_post(post_id):
    """Update a unified post"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        unified_post = UnifiedPost.query.filter_by(
            id=post_id,
            user_id=user_id
        ).first()
        
        if not unified_post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Check if post can be updated
        if unified_post.status in [PostStatus.PUBLISHED, PostStatus.PUBLISHING]:
            return jsonify({'error': 'Cannot update published or publishing posts'}), 400
        
        # Update fields
        updatable_fields = [
            'title', 'body', 'summary', 'media_items', 'tags', 'mentions',
            'links', 'location', 'category', 'language', 'platform_configs',
            'seo_title', 'seo_description', 'utm_source', 'utm_medium',
            'utm_campaign', 'utm_content'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(unified_post, field, data[field])
        
        # Handle scheduled time update
        if 'scheduled_time' in data:
            if data['scheduled_time']:
                try:
                    scheduled_time = datetime.fromisoformat(data['scheduled_time'].replace('Z', '+00:00'))
                    unified_post.scheduled_time = scheduled_time
                    unified_post.status = PostStatus.SCHEDULED
                except ValueError:
                    return jsonify({'error': 'Invalid scheduled_time format'}), 400
            else:
                unified_post.scheduled_time = None
                unified_post.status = PostStatus.DRAFT
        
        # Handle target platforms update
        if 'target_platforms' in data:
            valid_platforms = []
            for platform_name in data['target_platforms']:
                try:
                    platform = PlatformType(platform_name.lower())
                    valid_platforms.append(platform.value)
                except ValueError:
                    return jsonify({'error': f'Invalid platform: {platform_name}'}), 400
            
            unified_post.target_platforms = valid_platforms
            
            # Update platform posts
            existing_platforms = {pp.platform.value for pp in unified_post.platform_posts}
            new_platforms = set(valid_platforms)
            
            # Remove platform posts for platforms no longer targeted
            for platform_post in unified_post.platform_posts:
                if platform_post.platform.value not in new_platforms:
                    db.session.delete(platform_post)
            
            # Add platform posts for new platforms
            for platform_name in new_platforms - existing_platforms:
                platform_post = PlatformPost(
                    unified_post_id=unified_post.id,
                    platform=PlatformType(platform_name),
                    status=unified_post.status,
                    scheduled_time=unified_post.scheduled_time
                )
                db.session.add(platform_post)
        
        unified_post.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Generate updated previews
        platform_enums = [PlatformType(p) for p in unified_post.target_platforms]
        previews = preview_transformed_content(unified_post, platform_enums)
        
        response_data = unified_post.to_dict()
        response_data['platform_posts'] = [pp.to_dict() for pp in unified_post.platform_posts]
        response_data['previews'] = previews
        
        return jsonify({
            'message': 'Post updated successfully',
            'post': response_data
        })
        
    except Exception as e:
        logger.error(f"Error updating unified post: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@unified_posts_bp.route('/posts/<int:post_id>/publish', methods=['POST'])
@jwt_required()
def publish_unified_post(post_id):
    """Immediately publish a unified post"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        unified_post = UnifiedPost.query.filter_by(
            id=post_id,
            user_id=user_id
        ).first()
        
        if not unified_post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Check if post can be published
        if unified_post.status in [PostStatus.PUBLISHED, PostStatus.PUBLISHING]:
            return jsonify({'error': 'Post is already published or publishing'}), 400
        
        # Determine platforms to publish to
        target_platforms = data.get('platforms', unified_post.target_platforms)
        
        # Validate platforms
        valid_platforms = []
        for platform_name in target_platforms:
            if platform_name in unified_post.target_platforms:
                valid_platforms.append(platform_name)
        
        if not valid_platforms:
            return jsonify({'error': 'No valid platforms specified'}), 400
        
        # Create immediate publish jobs
        job_ids = []
        for platform_name in valid_platforms:
            job = create_post_job(
                unified_post.id,
                platform_name,
                user_id,
                priority=JobPriority.HIGH
            )
            job_id = queue_manager.enqueue(job)
            job_ids.append(job_id)
        
        # Update post status
        unified_post.status = PostStatus.QUEUED
        unified_post.updated_at = datetime.utcnow()
        
        # Update platform posts
        for platform_post in unified_post.platform_posts:
            if platform_post.platform.value in valid_platforms:
                platform_post.status = PostStatus.QUEUED
        
        db.session.commit()
        
        return jsonify({
            'message': 'Post queued for publishing',
            'post_id': post_id,
            'platforms': valid_platforms,
            'job_ids': job_ids,
            'status': 'queued'
        })
        
    except Exception as e:
        logger.error(f"Error publishing unified post: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@unified_posts_bp.route('/posts/<int:post_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_unified_post(post_id):
    """Cancel a scheduled unified post"""
    try:
        user_id = get_jwt_identity()
        
        unified_post = UnifiedPost.query.filter_by(
            id=post_id,
            user_id=user_id
        ).first()
        
        if not unified_post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Check if post can be cancelled
        if unified_post.status not in [PostStatus.SCHEDULED, PostStatus.QUEUED]:
            return jsonify({'error': 'Only scheduled or queued posts can be cancelled'}), 400
        
        # Update post status
        unified_post.status = PostStatus.CANCELLED
        unified_post.updated_at = datetime.utcnow()
        
        # Update platform posts
        for platform_post in unified_post.platform_posts:
            if platform_post.status in [PostStatus.SCHEDULED, PostStatus.QUEUED]:
                platform_post.status = PostStatus.CANCELLED
        
        db.session.commit()
        
        # TODO: Cancel queue jobs if they exist
        
        return jsonify({
            'message': 'Post cancelled successfully',
            'post_id': post_id,
            'status': 'cancelled'
        })
        
    except Exception as e:
        logger.error(f"Error cancelling unified post: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@unified_posts_bp.route('/posts/<int:post_id>/preview', methods=['GET'])
@jwt_required()
def preview_unified_post(post_id):
    """Preview how a post will look on different platforms"""
    try:
        user_id = get_jwt_identity()
        
        unified_post = UnifiedPost.query.filter_by(
            id=post_id,
            user_id=user_id
        ).first()
        
        if not unified_post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Get platforms to preview
        platforms_param = request.args.get('platforms')
        if platforms_param:
            platform_names = platforms_param.split(',')
            platforms = []
            for name in platform_names:
                try:
                    platforms.append(PlatformType(name.strip().lower()))
                except ValueError:
                    continue
        else:
            platforms = [PlatformType(p) for p in unified_post.target_platforms]
        
        # Generate previews
        previews = preview_transformed_content(unified_post, platforms)
        
        return jsonify({
            'post_id': post_id,
            'previews': previews
        })
        
    except Exception as e:
        logger.error(f"Error previewing unified post: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@unified_posts_bp.route('/posts/<int:post_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_unified_post(post_id):
    """Duplicate a unified post"""
    try:
        user_id = get_jwt_identity()
        
        original_post = UnifiedPost.query.filter_by(
            id=post_id,
            user_id=user_id
        ).first()
        
        if not original_post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Create duplicate
        duplicate_post = UnifiedPost(
            user_id=user_id,
            title=f"Copy of {original_post.title}" if original_post.title else None,
            body=original_post.body,
            summary=original_post.summary,
            media_items=original_post.media_items.copy() if original_post.media_items else [],
            tags=original_post.tags.copy() if original_post.tags else [],
            mentions=original_post.mentions.copy() if original_post.mentions else [],
            links=original_post.links.copy() if original_post.links else [],
            location=original_post.location.copy() if original_post.location else None,
            post_type=original_post.post_type,
            category=original_post.category,
            language=original_post.language,
            target_platforms=original_post.target_platforms.copy(),
            platform_configs=original_post.platform_configs.copy() if original_post.platform_configs else {},
            status=PostStatus.DRAFT,
            seo_title=original_post.seo_title,
            seo_description=original_post.seo_description,
            utm_source=original_post.utm_source,
            utm_medium=original_post.utm_medium,
            utm_campaign=original_post.utm_campaign,
            utm_content=original_post.utm_content
        )
        
        db.session.add(duplicate_post)
        db.session.commit()
        
        return jsonify({
            'message': 'Post duplicated successfully',
            'original_post_id': post_id,
            'duplicate_post_id': duplicate_post.id,
            'post': duplicate_post.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error duplicating unified post: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@unified_posts_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_unified_post(post_id):
    """Delete a unified post"""
    try:
        user_id = get_jwt_identity()
        
        unified_post = UnifiedPost.query.filter_by(
            id=post_id,
            user_id=user_id
        ).first()
        
        if not unified_post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Check if post can be deleted
        if unified_post.status == PostStatus.PUBLISHING:
            return jsonify({'error': 'Cannot delete post that is currently publishing'}), 400
        
        # Delete the post (cascade will handle platform posts)
        db.session.delete(unified_post)
        db.session.commit()
        
        return jsonify({
            'message': 'Post deleted successfully',
            'post_id': post_id
        })
        
    except Exception as e:
        logger.error(f"Error deleting unified post: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@unified_posts_bp.route('/mcp/<tool_name>', methods=['POST'])
@jwt_required()
def execute_mcp_tool(tool_name):
    """Execute MCP tool"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Add user_id to the data
        data['user_id'] = user_id
        
        # Execute the tool
        result = mcp_registry.execute(tool_name, **data)
        
        return jsonify(result.to_dict())
        
    except Exception as e:
        logger.error(f"Error executing MCP tool {tool_name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@unified_posts_bp.route('/mcp/tools', methods=['GET'])
@jwt_required()
def list_mcp_tools():
    """List available MCP tools"""
    try:
        tools = mcp_registry.list_tools()
        
        # Get schemas for each tool
        tool_schemas = {}
        for tool_name in tools:
            tool_schemas[tool_name] = mcp_registry.get_tool_schema(tool_name)
        
        return jsonify({
            'tools': tools,
            'schemas': tool_schemas
        })
        
    except Exception as e:
        logger.error(f"Error listing MCP tools: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

