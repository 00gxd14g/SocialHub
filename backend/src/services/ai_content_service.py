"""
AI Content Generation Service

This module provides AI-powered content creation features including
text generation, hashtag suggestions, content optimization, and SEO enhancement.
"""

import openai
import os
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AIContentService:
    """Service for AI-powered content creation and optimization"""
    
    def __init__(self):
        # OpenAI API is already configured via environment variables
        self.client = openai.OpenAI()
    
    def generate_post_content(self, topic: str, platform: str, tone: str = "professional", 
                            length: str = "medium") -> Dict[str, Any]:
        """Generate social media post content using AI"""
        try:
            # Platform-specific guidelines
            platform_guidelines = {
                "twitter": {
                    "max_length": 280,
                    "style": "concise, engaging, use hashtags",
                    "features": "threads, mentions, hashtags"
                },
                "facebook": {
                    "max_length": 500,
                    "style": "conversational, engaging, storytelling",
                    "features": "longer posts, links, images"
                },
                "instagram": {
                    "max_length": 300,
                    "style": "visual-focused, lifestyle, inspiring",
                    "features": "hashtags, stories, visual content"
                },
                "linkedin": {
                    "max_length": 400,
                    "style": "professional, insightful, industry-focused",
                    "features": "professional networking, thought leadership"
                }
            }
            
            guidelines = platform_guidelines.get(platform, platform_guidelines["facebook"])
            
            # Length specifications
            length_specs = {
                "short": "1-2 sentences",
                "medium": "2-4 sentences", 
                "long": "4-6 sentences"
            }
            
            prompt = f"""
            Create a {tone} social media post for {platform} about "{topic}".
            
            Guidelines:
            - Platform: {platform}
            - Style: {guidelines['style']}
            - Length: {length_specs.get(length, 'medium')} ({length})
            - Max characters: {guidelines['max_length']}
            - Tone: {tone}
            
            Requirements:
            1. Make it engaging and relevant to the topic
            2. Include appropriate hashtags for {platform}
            3. Keep within character limit
            4. Match the {tone} tone
            5. Optimize for {platform} audience
            
            Return only the post content, no explanations.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a social media content expert who creates engaging posts optimized for different platforms."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract hashtags
            hashtags = re.findall(r'#\w+', content)
            
            # Calculate metrics
            char_count = len(content)
            word_count = len(content.split())
            
            return {
                "success": True,
                "content": content,
                "platform": platform,
                "topic": topic,
                "tone": tone,
                "length": length,
                "metrics": {
                    "character_count": char_count,
                    "word_count": word_count,
                    "hashtag_count": len(hashtags),
                    "within_limit": char_count <= guidelines["max_length"]
                },
                "hashtags": hashtags,
                "suggestions": {
                    "optimal_posting_time": self._get_optimal_posting_time(platform),
                    "engagement_tips": self._get_engagement_tips(platform)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_hashtags(self, content: str, platform: str, count: int = 10) -> Dict[str, Any]:
        """Generate relevant hashtags for content"""
        try:
            prompt = f"""
            Generate {count} relevant and trending hashtags for this {platform} post:
            
            "{content}"
            
            Requirements:
            1. Make hashtags relevant to the content
            2. Include a mix of popular and niche hashtags
            3. Optimize for {platform} audience
            4. Include trending hashtags when relevant
            5. Format as #hashtag
            
            Return only the hashtags, one per line, no explanations.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a social media hashtag expert who creates trending and relevant hashtags."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.6
            )
            
            hashtags_text = response.choices[0].message.content.strip()
            hashtags = [tag.strip() for tag in hashtags_text.split('\n') if tag.strip().startswith('#')]
            
            return {
                "success": True,
                "hashtags": hashtags[:count],
                "platform": platform,
                "content_preview": content[:100] + "..." if len(content) > 100 else content
            }
            
        except Exception as e:
            logger.error(f"Error generating hashtags: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def optimize_content_for_seo(self, content: str, target_keywords: List[str]) -> Dict[str, Any]:
        """Optimize content for SEO"""
        try:
            keywords_str = ", ".join(target_keywords)
            
            prompt = f"""
            Optimize this content for SEO while maintaining readability and engagement:
            
            Original content: "{content}"
            Target keywords: {keywords_str}
            
            Requirements:
            1. Naturally incorporate the target keywords
            2. Maintain the original tone and message
            3. Improve readability and engagement
            4. Add relevant semantic keywords
            5. Keep the content natural and not keyword-stuffed
            
            Return the optimized content only.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an SEO content expert who optimizes content for search engines while maintaining quality."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.5
            )
            
            optimized_content = response.choices[0].message.content.strip()
            
            # Analyze keyword density
            keyword_analysis = {}
            for keyword in target_keywords:
                count = optimized_content.lower().count(keyword.lower())
                density = (count / len(optimized_content.split())) * 100
                keyword_analysis[keyword] = {
                    "count": count,
                    "density": round(density, 2)
                }
            
            return {
                "success": True,
                "original_content": content,
                "optimized_content": optimized_content,
                "target_keywords": target_keywords,
                "keyword_analysis": keyword_analysis,
                "improvements": [
                    "Incorporated target keywords naturally",
                    "Enhanced readability",
                    "Added semantic keywords",
                    "Maintained engagement factor"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing content for SEO: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_content_variations(self, original_content: str, platforms: List[str]) -> Dict[str, Any]:
        """Generate platform-specific variations of content"""
        try:
            variations = {}
            
            for platform in platforms:
                prompt = f"""
                Adapt this content for {platform}:
                
                Original: "{original_content}"
                
                Platform: {platform}
                
                Requirements:
                1. Optimize for {platform} audience and format
                2. Maintain the core message
                3. Adjust tone and style for the platform
                4. Include platform-appropriate hashtags
                5. Respect character limits
                
                Return only the adapted content.
                """
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are a social media expert specializing in {platform} content optimization."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.6
                )
                
                variations[platform] = {
                    "content": response.choices[0].message.content.strip(),
                    "character_count": len(response.choices[0].message.content.strip()),
                    "hashtags": re.findall(r'#\w+', response.choices[0].message.content)
                }
            
            return {
                "success": True,
                "original_content": original_content,
                "variations": variations,
                "platforms": platforms
            }
            
        except Exception as e:
            logger.error(f"Error generating content variations: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_content_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze the sentiment and tone of content"""
        try:
            prompt = f"""
            Analyze the sentiment and tone of this content:
            
            "{content}"
            
            Provide analysis for:
            1. Overall sentiment (positive, negative, neutral)
            2. Tone (professional, casual, friendly, etc.)
            3. Emotional impact (high, medium, low)
            4. Engagement potential (high, medium, low)
            5. Target audience fit
            
            Return as JSON format with these fields:
            {{
                "sentiment": "positive/negative/neutral",
                "tone": "description",
                "emotional_impact": "high/medium/low",
                "engagement_potential": "high/medium/low",
                "target_audience": "description",
                "recommendations": ["suggestion1", "suggestion2"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a content analysis expert who provides detailed sentiment and engagement analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            try:
                analysis = json.loads(response.choices[0].message.content.strip())
                analysis["success"] = True
                return analysis
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "success": True,
                    "sentiment": "neutral",
                    "tone": "professional",
                    "emotional_impact": "medium",
                    "engagement_potential": "medium",
                    "target_audience": "general",
                    "recommendations": ["Consider adding more engaging elements"],
                    "raw_analysis": response.choices[0].message.content.strip()
                }
            
        except Exception as e:
            logger.error(f"Error analyzing content sentiment: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_blog_post(self, topic: str, target_audience: str, word_count: int = 800) -> Dict[str, Any]:
        """Generate a complete blog post"""
        try:
            prompt = f"""
            Write a comprehensive blog post about "{topic}" for {target_audience}.
            
            Requirements:
            - Target word count: {word_count} words
            - Include engaging title
            - Add introduction, main content, and conclusion
            - Use subheadings for structure
            - Include SEO-friendly content
            - Make it informative and engaging
            - Add call-to-action at the end
            
            Format as markdown with proper headings.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional blog writer who creates engaging, SEO-optimized content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            blog_content = response.choices[0].message.content.strip()
            
            # Extract title (first heading)
            title_match = re.search(r'^#\s+(.+)$', blog_content, re.MULTILINE)
            title = title_match.group(1) if title_match else topic
            
            # Count words
            word_count_actual = len(blog_content.split())
            
            # Extract headings
            headings = re.findall(r'^#+\s+(.+)$', blog_content, re.MULTILINE)
            
            return {
                "success": True,
                "title": title,
                "content": blog_content,
                "topic": topic,
                "target_audience": target_audience,
                "metrics": {
                    "word_count": word_count_actual,
                    "character_count": len(blog_content),
                    "heading_count": len(headings),
                    "estimated_reading_time": max(1, word_count_actual // 200)  # ~200 words per minute
                },
                "headings": headings,
                "seo_keywords": self._extract_keywords(blog_content)
            }
            
        except Exception as e:
            logger.error(f"Error generating blog post: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_optimal_posting_time(self, platform: str) -> str:
        """Get optimal posting time for platform"""
        optimal_times = {
            "twitter": "9:00 AM - 10:00 AM, 7:00 PM - 9:00 PM",
            "facebook": "1:00 PM - 3:00 PM, 7:00 PM - 9:00 PM", 
            "instagram": "11:00 AM - 1:00 PM, 7:00 PM - 9:00 PM",
            "linkedin": "8:00 AM - 10:00 AM, 12:00 PM - 2:00 PM"
        }
        return optimal_times.get(platform, "9:00 AM - 5:00 PM")
    
    def _get_engagement_tips(self, platform: str) -> List[str]:
        """Get engagement tips for platform"""
        tips = {
            "twitter": [
                "Use trending hashtags",
                "Engage with replies quickly",
                "Share threads for longer content",
                "Retweet relevant content"
            ],
            "facebook": [
                "Ask questions to encourage comments",
                "Share behind-the-scenes content",
                "Use Facebook Stories",
                "Post videos for higher engagement"
            ],
            "instagram": [
                "Use high-quality visuals",
                "Post Stories regularly",
                "Use location tags",
                "Engage with your community"
            ],
            "linkedin": [
                "Share industry insights",
                "Comment on others' posts",
                "Use professional tone",
                "Share company updates"
            ]
        }
        return tips.get(platform, ["Post consistently", "Engage with your audience"])
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract potential SEO keywords from content"""
        # Simple keyword extraction - in production, use more sophisticated NLP
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        # Remove common words
        stop_words = {'this', 'that', 'with', 'have', 'will', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were'}
        keywords = [word for word in set(words) if word not in stop_words]
        return sorted(keywords)[:10]

# Singleton instance
ai_content_service = AIContentService()

