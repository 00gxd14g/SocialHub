"""
Enhanced Social Media API Integrations
Implements proper OAuth flows, error handling, and platform-specific optimizations
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs, urlparse
import base64
import hashlib
import hmac
import os
from dataclasses import dataclass
from enum import Enum

from ..models.unified_post import PlatformType
from .platform_transformers import TransformerFactory

logger = logging.getLogger(__name__)

class AuthStatus(Enum):
    VALID = "valid"
    EXPIRED = "expired"
    INVALID = "invalid"
    REFRESH_NEEDED = "refresh_needed"

@dataclass
class APICredentials:
    """API credentials for social media platforms"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None
    scope: Optional[str] = None
    platform_user_id: Optional[str] = None
    username: Optional[str] = None

class BaseSocialAPI:
    """Base class for social media API integrations"""
    
    def __init__(self, platform: PlatformType):
        self.platform = platform
        self.base_url = ""
        self.api_version = ""
        self.rate_limits = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SocialHub/1.0'
        })
    
    def authenticate(self, credentials: APICredentials) -> AuthStatus:
        """Check if credentials are valid"""
        raise NotImplementedError
    
    def refresh_token(self, credentials: APICredentials) -> APICredentials:
        """Refresh access token"""
        raise NotImplementedError
    
    def post_content(self, credentials: APICredentials, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to platform"""
        raise NotImplementedError
    
    def upload_media(self, credentials: APICredentials, media_url: str, media_type: str) -> str:
        """Upload media and return platform media ID"""
        raise NotImplementedError
    
    def get_analytics(self, credentials: APICredentials, post_id: str) -> Dict[str, Any]:
        """Get analytics for a post"""
        raise NotImplementedError
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook payload"""
        raise NotImplementedError

class TwitterAPI(BaseSocialAPI):
    """Twitter API v2 integration"""
    
    def __init__(self):
        super().__init__(PlatformType.TWITTER)
        self.base_url = "https://api.twitter.com"
        self.api_version = "2"
        self.upload_url = "https://upload.twitter.com"
        
        # Rate limits (requests per 15-minute window)
        self.rate_limits = {
            'tweets': 300,
            'media_upload': 300,
            'user_lookup': 300
        }
    
    def authenticate(self, credentials: APICredentials) -> AuthStatus:
        """Verify Twitter credentials"""
        try:
            headers = {
                'Authorization': f'Bearer {credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(
                f"{self.base_url}/2/users/me",
                headers=headers
            )
            
            if response.status_code == 200:
                return AuthStatus.VALID
            elif response.status_code == 401:
                return AuthStatus.INVALID
            else:
                logger.error(f"Twitter auth check failed: {response.status_code} - {response.text}")
                return AuthStatus.INVALID
                
        except Exception as e:
            logger.error(f"Twitter authentication error: {str(e)}")
            return AuthStatus.INVALID
    
    def post_content(self, credentials: APICredentials, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post tweet using API v2"""
        try:
            headers = {
                'Authorization': f'Bearer {credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Handle media upload first if needed
            if content.get('media_upload_required') and content.get('media_items'):
                media_ids = []
                for media_item in content['media_items']:
                    media_id = self.upload_media(credentials, media_item['url'], media_item['type'])
                    if media_id:
                        media_ids.append(media_id)
                
                if media_ids:
                    content['data']['media'] = {'media_ids': media_ids}
            
            response = self.session.post(
                f"{self.base_url}/2/tweets",
                headers=headers,
                json=content['data']
            )
            
            if response.status_code == 201:
                result = response.json()
                return {
                    'success': True,
                    'platform_post_id': result['data']['id'],
                    'platform_url': f"https://twitter.com/i/status/{result['data']['id']}",
                    'response': result
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    'success': False,
                    'error': error_data.get('detail', f'HTTP {response.status_code}'),
                    'response': error_data
                }
                
        except Exception as e:
            logger.error(f"Twitter post error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_media(self, credentials: APICredentials, media_url: str, media_type: str) -> Optional[str]:
        """Upload media using chunked upload for large files"""
        try:
            # Download media first
            media_response = requests.get(media_url)
            if media_response.status_code != 200:
                logger.error(f"Failed to download media from {media_url}")
                return None
            
            media_data = media_response.content
            media_size = len(media_data)
            
            headers = {
                'Authorization': f'Bearer {credentials.access_token}'
            }
            
            # INIT phase
            init_data = {
                'command': 'INIT',
                'total_bytes': media_size,
                'media_type': media_type,
                'media_category': 'tweet_image' if 'image' in media_type else 'tweet_video'
            }
            
            init_response = self.session.post(
                f"{self.upload_url}/1.1/media/upload.json",
                headers=headers,
                data=init_data
            )
            
            if init_response.status_code != 202:
                logger.error(f"Media upload INIT failed: {init_response.text}")
                return None
            
            media_id = init_response.json()['media_id_string']
            
            # APPEND phase (chunked upload)
            chunk_size = 1024 * 1024  # 1MB chunks
            segment_index = 0
            
            for i in range(0, media_size, chunk_size):
                chunk = media_data[i:i + chunk_size]
                
                append_data = {
                    'command': 'APPEND',
                    'media_id': media_id,
                    'segment_index': segment_index
                }
                
                files = {
                    'media': chunk
                }
                
                append_response = self.session.post(
                    f"{self.upload_url}/1.1/media/upload.json",
                    headers=headers,
                    data=append_data,
                    files=files
                )
                
                if append_response.status_code != 204:
                    logger.error(f"Media upload APPEND failed: {append_response.text}")
                    return None
                
                segment_index += 1
            
            # FINALIZE phase
            finalize_data = {
                'command': 'FINALIZE',
                'media_id': media_id
            }
            
            finalize_response = self.session.post(
                f"{self.upload_url}/1.1/media/upload.json",
                headers=headers,
                data=finalize_data
            )
            
            if finalize_response.status_code != 201:
                logger.error(f"Media upload FINALIZE failed: {finalize_response.text}")
                return None
            
            # Check processing status for videos
            result = finalize_response.json()
            if 'processing_info' in result:
                media_id = self._wait_for_processing(credentials, media_id)
            
            return media_id
            
        except Exception as e:
            logger.error(f"Twitter media upload error: {str(e)}")
            return None
    
    def _wait_for_processing(self, credentials: APICredentials, media_id: str) -> Optional[str]:
        """Wait for video processing to complete"""
        headers = {
            'Authorization': f'Bearer {credentials.access_token}'
        }
        
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            status_response = self.session.get(
                f"{self.upload_url}/1.1/media/upload.json",
                headers=headers,
                params={
                    'command': 'STATUS',
                    'media_id': media_id
                }
            )
            
            if status_response.status_code != 200:
                logger.error(f"Media status check failed: {status_response.text}")
                return None
            
            status_data = status_response.json()
            processing_info = status_data.get('processing_info', {})
            state = processing_info.get('state')
            
            if state == 'succeeded':
                return media_id
            elif state == 'failed':
                error = processing_info.get('error', {})
                logger.error(f"Media processing failed: {error}")
                return None
            elif state == 'in_progress':
                check_after = processing_info.get('check_after_secs', 5)
                time.sleep(check_after)
                attempt += 1
            else:
                time.sleep(5)
                attempt += 1
        
        logger.error("Media processing timeout")
        return None

class InstagramAPI(BaseSocialAPI):
    """Instagram Graph API integration"""
    
    def __init__(self):
        super().__init__(PlatformType.INSTAGRAM)
        self.base_url = "https://graph.facebook.com"
        self.api_version = "v18.0"
        
        # Rate limits (requests per hour)
        self.rate_limits = {
            'media_creation': 200,
            'media_publish': 25,  # Per user per hour
            'insights': 200
        }
    
    def authenticate(self, credentials: APICredentials) -> AuthStatus:
        """Verify Instagram credentials"""
        try:
            params = {
                'fields': 'id,username,account_type',
                'access_token': credentials.access_token
            }
            
            response = self.session.get(
                f"{self.base_url}/{self.api_version}/me",
                params=params
            )
            
            if response.status_code == 200:
                return AuthStatus.VALID
            elif response.status_code == 401:
                return AuthStatus.INVALID
            else:
                logger.error(f"Instagram auth check failed: {response.status_code} - {response.text}")
                return AuthStatus.INVALID
                
        except Exception as e:
            logger.error(f"Instagram authentication error: {str(e)}")
            return AuthStatus.INVALID
    
    def post_content(self, credentials: APICredentials, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post to Instagram using container -> publish flow"""
        try:
            # Step 1: Create media container
            container_id = self._create_media_container(credentials, content)
            if not container_id:
                return {
                    'success': False,
                    'error': 'Failed to create media container'
                }
            
            # Step 2: Publish container
            return self._publish_media_container(credentials, container_id)
            
        except Exception as e:
            logger.error(f"Instagram post error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_media_container(self, credentials: APICredentials, content: Dict[str, Any]) -> Optional[str]:
        """Create Instagram media container"""
        try:
            endpoint = f"{self.base_url}/{self.api_version}/{credentials.platform_user_id}/media"
            
            data = content['data'].copy()
            data['access_token'] = credentials.access_token
            
            # Handle carousel posts
            if content.get('requires_children_creation'):
                children_ids = []
                for child_data in data.get('children', []):
                    child_data['access_token'] = credentials.access_token
                    child_response = self.session.post(endpoint, data=child_data)
                    
                    if child_response.status_code == 200:
                        children_ids.append(child_response.json()['id'])
                    else:
                        logger.error(f"Failed to create child container: {child_response.text}")
                        return None
                
                data['children'] = ','.join(children_ids)
                del data['children']  # Remove the original children data
            
            response = self.session.post(endpoint, data=data)
            
            if response.status_code == 200:
                return response.json()['id']
            else:
                logger.error(f"Instagram container creation failed: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Instagram container creation error: {str(e)}")
            return None
    
    def _publish_media_container(self, credentials: APICredentials, container_id: str) -> Dict[str, Any]:
        """Publish Instagram media container"""
        try:
            endpoint = f"{self.base_url}/{self.api_version}/{credentials.platform_user_id}/media_publish"
            
            data = {
                'creation_id': container_id,
                'access_token': credentials.access_token
            }
            
            response = self.session.post(endpoint, data=data)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result['id']
                
                return {
                    'success': True,
                    'platform_post_id': post_id,
                    'platform_url': f"https://www.instagram.com/p/{post_id}/",
                    'response': result
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    'success': False,
                    'error': error_data.get('error', {}).get('message', f'HTTP {response.status_code}'),
                    'response': error_data
                }
                
        except Exception as e:
            logger.error(f"Instagram publish error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

class FacebookAPI(BaseSocialAPI):
    """Facebook Pages API integration"""
    
    def __init__(self):
        super().__init__(PlatformType.FACEBOOK)
        self.base_url = "https://graph.facebook.com"
        self.api_version = "v18.0"
        
        # Rate limits (requests per hour)
        self.rate_limits = {
            'page_posts': 600,
            'photo_uploads': 600,
            'video_uploads': 600
        }
    
    def authenticate(self, credentials: APICredentials) -> AuthStatus:
        """Verify Facebook Page credentials"""
        try:
            params = {
                'fields': 'id,name,access_token',
                'access_token': credentials.access_token
            }
            
            response = self.session.get(
                f"{self.base_url}/{self.api_version}/{credentials.platform_user_id}",
                params=params
            )
            
            if response.status_code == 200:
                return AuthStatus.VALID
            elif response.status_code == 401:
                return AuthStatus.INVALID
            else:
                logger.error(f"Facebook auth check failed: {response.status_code} - {response.text}")
                return AuthStatus.INVALID
                
        except Exception as e:
            logger.error(f"Facebook authentication error: {str(e)}")
            return AuthStatus.INVALID
    
    def post_content(self, credentials: APICredentials, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post to Facebook Page"""
        try:
            endpoint_type = content['endpoint'].split('/')[-1]  # feed, photos, videos
            endpoint = f"{self.base_url}/{self.api_version}/{credentials.platform_user_id}/{endpoint_type}"
            
            data = content['data'].copy()
            data['access_token'] = credentials.access_token
            
            # Handle different post types
            if endpoint_type == 'videos':
                return self._upload_video(credentials, data)
            elif endpoint_type == 'photos':
                return self._upload_photo(credentials, data)
            elif endpoint_type == 'albums':
                return self._create_album(credentials, data, content.get('media_items', []))
            else:
                # Regular feed post
                response = self.session.post(endpoint, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    post_id = result['id']
                    
                    return {
                        'success': True,
                        'platform_post_id': post_id,
                        'platform_url': f"https://www.facebook.com/{post_id}",
                        'response': result
                    }
                else:
                    error_data = response.json() if response.content else {}
                    return {
                        'success': False,
                        'error': error_data.get('error', {}).get('message', f'HTTP {response.status_code}'),
                        'response': error_data
                    }
                    
        except Exception as e:
            logger.error(f"Facebook post error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _upload_photo(self, credentials: APICredentials, data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload photo to Facebook"""
        try:
            endpoint = f"{self.base_url}/{self.api_version}/{credentials.platform_user_id}/photos"
            
            # Download image
            image_response = requests.get(data['url'])
            if image_response.status_code != 200:
                return {
                    'success': False,
                    'error': 'Failed to download image'
                }
            
            files = {
                'source': image_response.content
            }
            
            form_data = {
                'message': data.get('message', ''),
                'access_token': credentials.access_token
            }
            
            response = self.session.post(endpoint, data=form_data, files=files)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'platform_post_id': result['id'],
                    'platform_url': f"https://www.facebook.com/photo.php?fbid={result['id']}",
                    'response': result
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    'success': False,
                    'error': error_data.get('error', {}).get('message', f'HTTP {response.status_code}'),
                    'response': error_data
                }
                
        except Exception as e:
            logger.error(f"Facebook photo upload error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _upload_video(self, credentials: APICredentials, data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload video to Facebook"""
        try:
            endpoint = f"{self.base_url}/{self.api_version}/{credentials.platform_user_id}/videos"
            
            # For large videos, use resumable upload
            video_response = requests.get(data['source'])
            if video_response.status_code != 200:
                return {
                    'success': False,
                    'error': 'Failed to download video'
                }
            
            files = {
                'source': video_response.content
            }
            
            form_data = {
                'description': data.get('message', ''),
                'access_token': credentials.access_token
            }
            
            response = self.session.post(endpoint, data=form_data, files=files)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'platform_post_id': result['id'],
                    'platform_url': f"https://www.facebook.com/watch/?v={result['id']}",
                    'response': result
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    'success': False,
                    'error': error_data.get('error', {}).get('message', f'HTTP {response.status_code}'),
                    'response': error_data
                }
                
        except Exception as e:
            logger.error(f"Facebook video upload error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

class LinkedInAPI(BaseSocialAPI):
    """LinkedIn API integration"""
    
    def __init__(self):
        super().__init__(PlatformType.LINKEDIN)
        self.base_url = "https://api.linkedin.com"
        self.api_version = "v2"
        
        # Rate limits (requests per hour)
        self.rate_limits = {
            'ugc_posts': 100,
            'media_upload': 100,
            'profile': 100
        }
    
    def authenticate(self, credentials: APICredentials) -> AuthStatus:
        """Verify LinkedIn credentials"""
        try:
            headers = {
                'Authorization': f'Bearer {credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(
                f"{self.base_url}/v2/people/~",
                headers=headers
            )
            
            if response.status_code == 200:
                return AuthStatus.VALID
            elif response.status_code == 401:
                return AuthStatus.INVALID
            else:
                logger.error(f"LinkedIn auth check failed: {response.status_code} - {response.text}")
                return AuthStatus.INVALID
                
        except Exception as e:
            logger.error(f"LinkedIn authentication error: {str(e)}")
            return AuthStatus.INVALID
    
    def post_content(self, credentials: APICredentials, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post to LinkedIn"""
        try:
            headers = {
                'Authorization': f'Bearer {credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Replace placeholder with actual person ID
            post_data = content['data']
            post_data['author'] = f"urn:li:person:{credentials.platform_user_id}"
            
            # Handle media upload if needed
            if content.get('requires_media_upload') and content.get('media_items'):
                media_assets = []
                for media_item in content['media_items']:
                    asset_id = self._upload_media(credentials, media_item['url'], media_item['type'])
                    if asset_id:
                        media_assets.append(f"urn:li:digitalmediaAsset:{asset_id}")
                
                if media_assets:
                    # Update post data with media assets
                    share_content = post_data['specificContent']['com.linkedin.ugc.ShareContent']
                    if 'media' in share_content:
                        for i, media_asset in enumerate(media_assets):
                            if i < len(share_content['media']):
                                share_content['media'][i]['media'] = media_asset
            
            response = self.session.post(
                f"{self.base_url}/v2/ugcPosts",
                headers=headers,
                json=post_data
            )
            
            if response.status_code == 201:
                result = response.json()
                post_id = result['id']
                
                return {
                    'success': True,
                    'platform_post_id': post_id,
                    'platform_url': f"https://www.linkedin.com/feed/update/{post_id}/",
                    'response': result
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    'success': False,
                    'error': error_data.get('message', f'HTTP {response.status_code}'),
                    'response': error_data
                }
                
        except Exception as e:
            logger.error(f"LinkedIn post error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _upload_media(self, credentials: APICredentials, media_url: str, media_type: str) -> Optional[str]:
        """Upload media to LinkedIn"""
        try:
            # Step 1: Register upload
            headers = {
                'Authorization': f'Bearer {credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            register_data = {
                'registerUploadRequest': {
                    'recipes': ['urn:li:digitalmediaRecipe:feedshare-image'],
                    'owner': f"urn:li:person:{credentials.platform_user_id}",
                    'serviceRelationships': [
                        {
                            'relationshipType': 'OWNER',
                            'identifier': 'urn:li:userGeneratedContent'
                        }
                    ]
                }
            }
            
            register_response = self.session.post(
                f"{self.base_url}/v2/assets?action=registerUpload",
                headers=headers,
                json=register_data
            )
            
            if register_response.status_code != 200:
                logger.error(f"LinkedIn media register failed: {register_response.text}")
                return None
            
            register_result = register_response.json()
            upload_url = register_result['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset_id = register_result['value']['asset']
            
            # Step 2: Upload media
            media_response = requests.get(media_url)
            if media_response.status_code != 200:
                logger.error(f"Failed to download media from {media_url}")
                return None
            
            upload_headers = {
                'Authorization': f'Bearer {credentials.access_token}'
            }
            
            upload_response = requests.put(
                upload_url,
                headers=upload_headers,
                data=media_response.content
            )
            
            if upload_response.status_code == 201:
                return asset_id.split(':')[-1]  # Extract asset ID
            else:
                logger.error(f"LinkedIn media upload failed: {upload_response.text}")
                return None
                
        except Exception as e:
            logger.error(f"LinkedIn media upload error: {str(e)}")
            return None

class SocialAPIManager:
    """Manager for all social media API integrations"""
    
    def __init__(self):
        self.apis = {
            PlatformType.TWITTER: TwitterAPI(),
            PlatformType.INSTAGRAM: InstagramAPI(),
            PlatformType.FACEBOOK: FacebookAPI(),
            PlatformType.LINKEDIN: LinkedInAPI(),
        }
    
    def get_api(self, platform: PlatformType) -> BaseSocialAPI:
        """Get API instance for platform"""
        api = self.apis.get(platform)
        if not api:
            raise ValueError(f"No API available for platform: {platform}")
        return api
    
    def publish_post(self, platform: PlatformType, credentials: APICredentials, 
                    unified_post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Publish post to specific platform"""
        try:
            # Get platform API
            api = self.get_api(platform)
            
            # Check authentication
            auth_status = api.authenticate(credentials)
            if auth_status != AuthStatus.VALID:
                return {
                    'success': False,
                    'error': f'Authentication failed: {auth_status.value}'
                }
            
            # Transform content for platform
            transformer = TransformerFactory.get_transformer(platform)
            transformed_content = transformer.transform(unified_post_data)
            
            # Validate content
            is_valid, errors = transformer.validate_content(transformed_content.get('data', {}))
            if not is_valid:
                return {
                    'success': False,
                    'error': f'Content validation failed: {", ".join(errors)}'
                }
            
            # Publish content
            result = api.post_content(credentials, transformed_content)
            
            return result
            
        except Exception as e:
            logger.error(f"Error publishing to {platform.value}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_analytics(self, platform: PlatformType, credentials: APICredentials, 
                     post_id: str) -> Dict[str, Any]:
        """Get analytics for a post"""
        try:
            api = self.get_api(platform)
            
            # Check authentication
            auth_status = api.authenticate(credentials)
            if auth_status != AuthStatus.VALID:
                return {
                    'success': False,
                    'error': f'Authentication failed: {auth_status.value}'
                }
            
            # Get analytics
            analytics = api.get_analytics(credentials, post_id)
            
            return {
                'success': True,
                'analytics': analytics
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics from {platform.value}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Global API manager instance
social_api_manager = SocialAPIManager()

