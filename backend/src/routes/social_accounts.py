from flask import Blueprint, request, jsonify, session
from src.models.user import User, db
from src.models.social_account import SocialAccount
from src.models.analytics import Analytics
from datetime import datetime, date, timedelta

social_accounts_bp = Blueprint('social_accounts', __name__)

def require_auth():
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

@social_accounts_bp.route('/social-accounts', methods=['GET'])
def get_social_accounts():
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        accounts = SocialAccount.query.filter_by(user_id=user.id).all()
        return jsonify({
            'accounts': [account.to_dict() for account in accounts]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch social accounts'}), 500

@social_accounts_bp.route('/social-accounts', methods=['POST'])
def add_social_account():
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        
        required_fields = ['platform', 'platform_user_id', 'username', 'access_token']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if account already exists
        existing_account = SocialAccount.query.filter_by(
            user_id=user.id,
            platform=data['platform'],
            platform_user_id=data['platform_user_id']
        ).first()
        
        if existing_account:
            return jsonify({'error': 'Account already connected'}), 400
        
        # Create new social account
        account = SocialAccount(
            user_id=user.id,
            platform=data['platform'],
            platform_user_id=data['platform_user_id'],
            username=data['username'],
            access_token=data['access_token'],
            refresh_token=data.get('refresh_token'),
            expires_at=datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00')) if data.get('expires_at') else None
        )
        
        db.session.add(account)
        db.session.commit()
        
        return jsonify({
            'message': 'Social account added successfully',
            'account': account.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add social account'}), 500

@social_accounts_bp.route('/social-accounts/<int:account_id>', methods=['PUT'])
def update_social_account(account_id):
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        account = SocialAccount.query.filter_by(id=account_id, user_id=user.id).first()
        if not account:
            return jsonify({'error': 'Social account not found'}), 404
        
        data = request.get_json()
        
        # Update account fields
        if 'access_token' in data:
            account.access_token = data['access_token']
        if 'refresh_token' in data:
            account.refresh_token = data['refresh_token']
        if 'expires_at' in data:
            account.expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00')) if data['expires_at'] else None
        if 'is_active' in data:
            account.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Social account updated successfully',
            'account': account.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update social account'}), 500

@social_accounts_bp.route('/social-accounts/<int:account_id>', methods=['DELETE'])
def delete_social_account(account_id):
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        account = SocialAccount.query.filter_by(id=account_id, user_id=user.id).first()
        if not account:
            return jsonify({'error': 'Social account not found'}), 404
        
        # Delete associated analytics
        Analytics.query.filter_by(social_account_id=account.id).delete()
        
        # Delete the account
        db.session.delete(account)
        db.session.commit()
        
        return jsonify({'message': 'Social account deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete social account'}), 500

@social_accounts_bp.route('/social-accounts/<int:account_id>/analytics', methods=['GET'])
def get_account_analytics(account_id):
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        account = SocialAccount.query.filter_by(id=account_id, user_id=user.id).first()
        if not account:
            return jsonify({'error': 'Social account not found'}), 404
        
        # Get date range from query parameters
        days = request.args.get('days', 30, type=int)
        start_date = date.today() - timedelta(days=days)
        
        analytics = Analytics.query.filter(
            Analytics.social_account_id == account.id,
            Analytics.date >= start_date
        ).order_by(Analytics.date.desc()).all()
        
        return jsonify({
            'analytics': [a.to_dict() for a in analytics]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch analytics'}), 500

