"""
Social Media API Integration Service

This module provides integration with various social media platforms
including Twitter, Facebook, Instagram, LinkedIn, and YouTube.
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

# Add the Manus API client path for accessing available APIs
sys.path.append('/opt/.manus/.sandbox-runtime')

try:
    from data_api import ApiClient
    MANUS_API_AVAILABLE = True
except ImportError:
    MANUS_API_AVAILABLE = False
    logging.warning("Manus API client not available. Some features may be limited.")

class SocialMediaAPIService:
    """Service for integrating with social media platforms"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if MANUS_API_AVAILABLE:
            self.api_client = ApiClient()
        else:
            self.api_client = None
    
    # Twitter Integration
    def get_twitter_profile(self, username: str) -> Dict[str, Any]:
        """Get Twitter user profile by username"""
        if not self.api_client:
            return {"error": "API client not available"}
        
        try:
            response = self.api_client.call_api(
                'Twitter/get_user_profile_by_username',
                query={'username': username}
            )
            return response
        except Exception as e:
            self.logger.error(f"Error fetching Twitter profile: {str(e)}")
            return {"error": str(e)}
    
    def search_twitter(self, query: str, count: int = 20) -> Dict[str, Any]:
        """Search Twitter for tweets"""
        if not self.api_client:
            return {"error": "API client not available"}
        
        try:
            response = self.api_client.call_api(
                'Twitter/search_twitter',
                query={'query': query, 'count': str(count)}
            )
            return response
        except Exception as e:
            self.logger.error(f"Error searching Twitter: {str(e)}")
            return {"error": str(e)}
    
    def get_user_tweets(self, user_id: str, count: int = 20) -> Dict[str, Any]:
        """Get tweets from a specific user"""
        if not self.api_client:
            return {"error": "API client not available"}
        
        try:
            response = self.api_client.call_api(
                'Twitter/get_user_tweets',
                query={'user': user_id, 'count': str(count)}
            )
            return response
        except Exception as e:
            self.logger.error(f"Error fetching user tweets: {str(e)}")
            return {"error": str(e)}
    
    # LinkedIn Integration
    def get_linkedin_profile(self, username: str) -> Dict[str, Any]:
        """Get LinkedIn profile by username"""
        if not self.api_client:
            return {"error": "API client not available"}
        
        try:
            response = self.api_client.call_api(
                'LinkedIn/get_user_profile_by_username',
                query={'username': username}
            )
            return response
        except Exception as e:
            self.logger.error(f"Error fetching LinkedIn profile: {str(e)}")
            return {"error": str(e)}
    
    def search_linkedin_people(self, keywords: str, **kwargs) -> Dict[str, Any]:
        """Search for people on LinkedIn"""
        if not self.api_client:
            return {"error": "API client not available"}
        
        try:
            query_params = {'keywords': keywords}
            query_params.update(kwargs)
            
            response = self.api_client.call_api(
                'LinkedIn/search_people',
                query=query_params
            )
            return response
        except Exception as e:
            self.logger.error(f"Error searching LinkedIn people: {str(e)}")
            return {"error": str(e)}
    
    # YouTube Integration
    def search_youtube(self, query: str, language: str = "en", country: str = "US") -> Dict[str, Any]:
        """Search YouTube content"""
        if not self.api_client:
            return {"error": "API client not available"}
        
        try:
            response = self.api_client.call_api(
                'Youtube/search',
                query={'q': query, 'hl': language, 'gl': country}
            )
            return response
        except Exception as e:
            self.logger.error(f"Error searching YouTube: {str(e)}")
            return {"error": str(e)}
    
    def get_youtube_channel_details(self, channel_id: str, language: str = "en") -> Dict[str, Any]:
        """Get YouTube channel details"""
        if not self.api_client:
            return {"error": "API client not available"}
        
        try:
            response = self.api_client.call_api(
                'Youtube/get_channel_details',
                query={'id': channel_id, 'hl': language}
            )
            return response
        except Exception as e:
            self.logger.error(f"Error fetching YouTube channel details: {str(e)}")
            return {"error": str(e)}
    
    def get_youtube_channel_videos(self, channel_id: str, filter_type: str = "videos_latest") -> Dict[str, Any]:
        """Get videos from a YouTube channel"""
        if not self.api_client:
            return {"error": "API client not available"}
        
        try:
            response = self.api_client.call_api(
                'Youtube/get_channel_videos',
                query={'id': channel_id, 'filter': filter_type}
            )
            return response
        except Exception as e:
            self.logger.error(f"Error fetching YouTube channel videos: {str(e)}")
            return {"error": str(e)}
    
    # Facebook/Meta Integration (using Graph API)
    def post_to_facebook_page(self, page_id: str, access_token: str, message: str, 
                             link: Optional[str] = None, scheduled_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Post to a Facebook page"""
        try:
            url = f"https://graph.facebook.com/v23.0/{page_id}/feed"
            
            data = {
                "message": message,
                "access_token": access_token
            }
            
            if link:
                data["link"] = link
            
            if scheduled_time:
                data["published"] = "false"
                data["scheduled_publish_time"] = int(scheduled_time.timestamp())
            else:
                data["published"] = "true"
            
            response = requests.post(url, data=data)
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error posting to Facebook: {str(e)}")
            return {"error": str(e)}
    
    def get_facebook_page_posts(self, page_id: str, access_token: str) -> Dict[str, Any]:
        """Get posts from a Facebook page"""
        try:
            url = f"https://graph.facebook.com/v23.0/{page_id}/feed"
            params = {"access_token": access_token}
            
            response = requests.get(url, params=params)
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error fetching Facebook posts: {str(e)}")
            return {"error": str(e)}
    
    def post_photo_to_facebook(self, page_id: str, access_token: str, photo_url: str, 
                              caption: Optional[str] = None) -> Dict[str, Any]:
        """Post a photo to Facebook page"""
        try:
            url = f"https://graph.facebook.com/v23.0/{page_id}/photos"
            
            data = {
                "url": photo_url,
                "access_token": access_token
            }
            
            if caption:
                data["caption"] = caption
            
            response = requests.post(url, data=data)
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error posting photo to Facebook: {str(e)}")
            return {"error": str(e)}
    
    # Instagram Integration (Note: Basic Display API is deprecated)
    def get_instagram_media(self, access_token: str) -> Dict[str, Any]:
        """Get Instagram media (limited due to API deprecation)"""
        try:
            # Note: Instagram Basic Display API was deprecated in December 2024
            # This is a placeholder for future Instagram Graph API integration
            return {
                "error": "Instagram Basic Display API has been deprecated. Please use Instagram Graph API for business accounts."
            }
        except Exception as e:
            self.logger.error(f"Error fetching Instagram media: {str(e)}")
            return {"error": str(e)}
    
    # Content Creation and AI Features
    def generate_hashtags(self, content: str, platform: str = "general") -> List[str]:
        """Generate relevant hashtags for content"""
        # This is a simple implementation - in production, you might use AI services
        common_hashtags = {
            "twitter": ["#socialmedia", "#marketing", "#content", "#engagement"],
            "instagram": ["#insta", "#photo", "#lifestyle", "#follow"],
            "linkedin": ["#professional", "#business", "#networking", "#career"],
            "general": ["#social", "#content", "#digital", "#online"]
        }
        
        # Extract keywords from content and suggest hashtags
        words = content.lower().split()
        suggested = []
        
        # Add platform-specific hashtags
        suggested.extend(common_hashtags.get(platform, common_hashtags["general"]))
        
        # Add content-based hashtags (simple keyword matching)
        if "ai" in content.lower():
            suggested.append("#AI")
        if "tech" in content.lower():
            suggested.append("#technology")
        if "business" in content.lower():
            suggested.append("#business")
        
        return list(set(suggested))[:10]  # Return unique hashtags, max 10
    
    def optimize_content_for_platform(self, content: str, platform: str) -> Dict[str, Any]:
        """Optimize content for specific platform"""
        optimizations = {
            "twitter": {
                "max_length": 280,
                "suggestions": ["Keep it concise", "Use hashtags", "Add mentions"]
            },
            "facebook": {
                "max_length": 63206,
                "suggestions": ["Engage with questions", "Use emojis", "Add links"]
            },
            "instagram": {
                "max_length": 2200,
                "suggestions": ["Use visual content", "Add hashtags", "Tell a story"]
            },
            "linkedin": {
                "max_length": 3000,
                "suggestions": ["Be professional", "Share insights", "Network"]
            }
        }
        
        platform_info = optimizations.get(platform, optimizations["facebook"])
        
        result = {
            "original_content": content,
            "platform": platform,
            "character_count": len(content),
            "max_length": platform_info["max_length"],
            "within_limit": len(content) <= platform_info["max_length"],
            "suggestions": platform_info["suggestions"],
            "hashtags": self.generate_hashtags(content, platform)
        }
        
        # Truncate if too long
        if not result["within_limit"]:
            result["optimized_content"] = content[:platform_info["max_length"]-3] + "..."
        else:
            result["optimized_content"] = content
        
        return result
    
    # Analytics and Insights
    def get_platform_analytics(self, platform: str, account_id: str, access_token: str) -> Dict[str, Any]:
        """Get analytics for a specific platform"""
        # This is a placeholder for analytics integration
        # In production, you would integrate with each platform's analytics API
        
        mock_analytics = {
            "platform": platform,
            "account_id": account_id,
            "period": "last_30_days",
            "metrics": {
                "followers": 1250,
                "engagement_rate": 3.5,
                "reach": 15000,
                "impressions": 25000,
                "clicks": 450
            },
            "top_posts": [
                {"id": "post_1", "engagement": 150, "reach": 2000},
                {"id": "post_2", "engagement": 120, "reach": 1800}
            ]
        }
        
        return mock_analytics
    
    # Cross-platform posting
    def post_to_multiple_platforms(self, content: str, platforms: List[str], 
                                  access_tokens: Dict[str, str], 
                                  scheduled_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Post content to multiple platforms simultaneously"""
        results = {}
        
        for platform in platforms:
            try:
                optimized = self.optimize_content_for_platform(content, platform)
                optimized_content = optimized["optimized_content"]
                
                if platform == "facebook" and "facebook" in access_tokens:
                    # Assuming we have page_id stored somewhere
                    page_id = "your_page_id"  # This should come from user's connected accounts
                    result = self.post_to_facebook_page(
                        page_id, access_tokens["facebook"], 
                        optimized_content, scheduled_time=scheduled_time
                    )
                    results[platform] = result
                
                elif platform == "twitter":
                    # Twitter posting would require Twitter API v2 with write permissions
                    results[platform] = {"error": "Twitter posting requires API v2 with write permissions"}
                
                elif platform == "instagram":
                    # Instagram posting requires Instagram Graph API for business accounts
                    results[platform] = {"error": "Instagram posting requires Graph API for business accounts"}
                
                elif platform == "linkedin":
                    # LinkedIn posting requires LinkedIn API
                    results[platform] = {"error": "LinkedIn posting requires LinkedIn API integration"}
                
                else:
                    results[platform] = {"error": f"Platform {platform} not supported"}
                    
            except Exception as e:
                results[platform] = {"error": str(e)}
        
        return {
            "original_content": content,
            "platforms": platforms,
            "scheduled_time": scheduled_time.isoformat() if scheduled_time else None,
            "results": results
        }

# Singleton instance
social_media_service = SocialMediaAPIService()

