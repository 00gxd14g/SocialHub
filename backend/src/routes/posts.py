from flask import Blueprint, request, jsonify, session
from src.models.user import User, db
from src.models.post import Post, PostPlatform
from src.models.social_account import SocialAccount
from datetime import datetime
import json

posts_bp = Blueprint('posts', __name__)

def require_auth():
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

@posts_bp.route('/posts', methods=['GET'])
def get_posts():
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
        return jsonify({
            'posts': [post.to_dict() for post in posts]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch posts'}), 500

@posts_bp.route('/posts', methods=['POST'])
def create_post():
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'error': 'Content is required'}), 400
        
        # Create new post
        post = Post(
            user_id=user.id,
            content=data['content'],
            media_urls=json.dumps(data.get('media_urls', [])),
            hashtags=json.dumps(data.get('hashtags', [])),
            status='draft'
        )
        
        # Set scheduled time if provided
        if data.get('scheduled_at'):
            try:
                post.scheduled_at = datetime.fromisoformat(data['scheduled_at'].replace('Z', '+00:00'))
                post.status = 'scheduled'
            except ValueError:
                return jsonify({'error': 'Invalid scheduled_at format'}), 400
        
        db.session.add(post)
        db.session.flush()  # Get the post ID
        
        # Create post platform associations
        selected_accounts = data.get('selected_accounts', [])
        for account_id in selected_accounts:
            # Verify account belongs to user
            account = SocialAccount.query.filter_by(
                id=account_id, 
                user_id=user.id, 
                is_active=True
            ).first()
            
            if account:
                post_platform = PostPlatform(
                    post_id=post.id,
                    social_account_id=account.id,
                    status='pending'
                )
                db.session.add(post_platform)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Post created successfully',
            'post': post.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create post'}), 500

@posts_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        post = Post.query.filter_by(id=post_id, user_id=user.id).first()
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Get post platforms
        post_platforms = PostPlatform.query.filter_by(post_id=post.id).all()
        post_data = post.to_dict()
        post_data['platforms'] = [pp.to_dict() for pp in post_platforms]
        
        return jsonify({'post': post_data}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch post'}), 500

@posts_bp.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        post = Post.query.filter_by(id=post_id, user_id=user.id).first()
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        data = request.get_json()
        
        # Update post fields
        if 'content' in data:
            post.content = data['content']
        if 'media_urls' in data:
            post.media_urls = json.dumps(data['media_urls'])
        if 'hashtags' in data:
            post.hashtags = json.dumps(data['hashtags'])
        if 'scheduled_at' in data:
            if data['scheduled_at']:
                try:
                    post.scheduled_at = datetime.fromisoformat(data['scheduled_at'].replace('Z', '+00:00'))
                    post.status = 'scheduled'
                except ValueError:
                    return jsonify({'error': 'Invalid scheduled_at format'}), 400
            else:
                post.scheduled_at = None
                post.status = 'draft'
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Post updated successfully',
            'post': post.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update post'}), 500

@posts_bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        post = Post.query.filter_by(id=post_id, user_id=user.id).first()
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Delete associated post platforms
        PostPlatform.query.filter_by(post_id=post.id).delete()
        
        # Delete the post
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': 'Post deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete post'}), 500

