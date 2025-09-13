"""
SEO Optimization Service

This module provides SEO-related features including keyword analysis,
content optimization, meta tag generation, and SEO scoring.
"""

import re
import openai
from typing import Dict, Any, List, Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class SEOService:
    """Service for SEO optimization and analysis"""
    
    def __init__(self):
        self.client = openai.OpenAI()
        
        # Common stop words to exclude from keyword analysis
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
            'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her',
            'its', 'our', 'their'
        }
    
    def analyze_content_seo(self, content: str, target_keywords: List[str] = None) -> Dict[str, Any]:
        """Analyze content for SEO factors"""
        try:
            # Basic content metrics
            word_count = len(content.split())
            char_count = len(content)
            sentence_count = len(re.split(r'[.!?]+', content))
            paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
            
            # Extract keywords from content
            extracted_keywords = self._extract_keywords(content)
            
            # Analyze keyword density
            keyword_density = {}
            if target_keywords:
                for keyword in target_keywords:
                    count = content.lower().count(keyword.lower())
                    density = (count / word_count) * 100 if word_count > 0 else 0
                    keyword_density[keyword] = {
                        'count': count,
                        'density': round(density, 2)
                    }
            
            # Calculate readability score (simplified Flesch Reading Ease)
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            readability_score = self._calculate_readability(content, word_count, sentence_count)
            
            # SEO score calculation
            seo_score = self._calculate_seo_score(
                word_count, keyword_density, readability_score, content
            )
            
            return {
                'success': True,
                'metrics': {
                    'word_count': word_count,
                    'character_count': char_count,
                    'sentence_count': sentence_count,
                    'paragraph_count': paragraph_count,
                    'avg_sentence_length': round(avg_sentence_length, 1),
                    'readability_score': readability_score
                },
                'keywords': {
                    'extracted': extracted_keywords[:10],  # Top 10 keywords
                    'target_analysis': keyword_density
                },
                'seo_score': seo_score,
                'recommendations': self._generate_seo_recommendations(
                    word_count, keyword_density, readability_score, content
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content SEO: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_meta_tags(self, content: str, title: str = None) -> Dict[str, Any]:
        """Generate SEO meta tags for content"""
        try:
            prompt = f"""
            Generate SEO meta tags for this content:
            
            Title: {title or 'Not provided'}
            Content: {content[:500]}...
            
            Generate:
            1. Meta title (50-60 characters)
            2. Meta description (150-160 characters)
            3. Keywords (5-10 relevant keywords)
            4. Open Graph title
            5. Open Graph description
            
            Return as JSON format:
            {{
                "meta_title": "...",
                "meta_description": "...",
                "keywords": ["keyword1", "keyword2", ...],
                "og_title": "...",
                "og_description": "..."
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an SEO expert who creates optimized meta tags."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            try:
                import json
                meta_tags = json.loads(response.choices[0].message.content.strip())
                
                # Validate and clean up the response
                meta_tags['meta_title'] = meta_tags.get('meta_title', title or 'Untitled')[:60]
                meta_tags['meta_description'] = meta_tags.get('meta_description', '')[:160]
                meta_tags['keywords'] = meta_tags.get('keywords', [])[:10]
                
                return {
                    'success': True,
                    'meta_tags': meta_tags
                }
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._generate_fallback_meta_tags(content, title)
            
        except Exception as e:
            logger.error(f"Error generating meta tags: {str(e)}")
            return self._generate_fallback_meta_tags(content, title)
    
    def optimize_content_for_keywords(self, content: str, target_keywords: List[str]) -> Dict[str, Any]:
        """Optimize content for specific keywords"""
        try:
            keywords_str = ", ".join(target_keywords)
            
            prompt = f"""
            Optimize this content for SEO while maintaining readability and natural flow:
            
            Original content: "{content}"
            Target keywords: {keywords_str}
            
            Requirements:
            1. Naturally incorporate target keywords (aim for 1-3% density)
            2. Maintain the original message and tone
            3. Improve readability and structure
            4. Add semantic keywords related to the target keywords
            5. Ensure content flows naturally
            
            Return the optimized content only.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an SEO content expert who optimizes content for search engines while maintaining quality."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.5
            )
            
            optimized_content = response.choices[0].message.content.strip()
            
            # Analyze the optimization
            original_analysis = self.analyze_content_seo(content, target_keywords)
            optimized_analysis = self.analyze_content_seo(optimized_content, target_keywords)
            
            return {
                'success': True,
                'original_content': content,
                'optimized_content': optimized_content,
                'target_keywords': target_keywords,
                'analysis': {
                    'original': original_analysis,
                    'optimized': optimized_analysis
                },
                'improvements': self._calculate_improvements(original_analysis, optimized_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error optimizing content: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_schema_markup(self, content_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON-LD schema markup"""
        try:
            schema_templates = {
                'article': {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    "headline": data.get('title', ''),
                    "description": data.get('description', ''),
                    "author": {
                        "@type": "Person",
                        "name": data.get('author', 'Unknown')
                    },
                    "datePublished": data.get('date_published', ''),
                    "dateModified": data.get('date_modified', ''),
                    "publisher": {
                        "@type": "Organization",
                        "name": data.get('publisher', 'SocialHub')
                    }
                },
                'organization': {
                    "@context": "https://schema.org",
                    "@type": "Organization",
                    "name": data.get('name', ''),
                    "description": data.get('description', ''),
                    "url": data.get('url', ''),
                    "logo": data.get('logo', ''),
                    "sameAs": data.get('social_profiles', [])
                },
                'website': {
                    "@context": "https://schema.org",
                    "@type": "WebSite",
                    "name": data.get('name', ''),
                    "description": data.get('description', ''),
                    "url": data.get('url', ''),
                    "potentialAction": {
                        "@type": "SearchAction",
                        "target": f"{data.get('url', '')}/search?q={{search_term_string}}",
                        "query-input": "required name=search_term_string"
                    }
                }
            }
            
            schema = schema_templates.get(content_type, {})
            
            return {
                'success': True,
                'schema_markup': schema,
                'content_type': content_type
            }
            
        except Exception as e:
            logger.error(f"Error generating schema markup: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_competitor_content(self, competitor_urls: List[str], target_keywords: List[str]) -> Dict[str, Any]:
        """Analyze competitor content for SEO insights"""
        # This is a placeholder for competitor analysis
        # In a real implementation, you would scrape competitor pages and analyze them
        
        mock_analysis = {
            'success': True,
            'competitors_analyzed': len(competitor_urls),
            'target_keywords': target_keywords,
            'insights': {
                'avg_content_length': 1200,
                'common_keywords': ['social media', 'marketing', 'engagement', 'content'],
                'content_gaps': ['AI automation', 'analytics insights', 'cross-platform'],
                'recommended_topics': [
                    'Social Media Automation with AI',
                    'Cross-Platform Analytics Guide',
                    'Content Optimization Strategies'
                ]
            },
            'recommendations': [
                'Create longer-form content (1000+ words)',
                'Focus on AI and automation keywords',
                'Include more technical depth',
                'Add case studies and examples'
            ]
        }
        
        return mock_analysis
    
    def _extract_keywords(self, content: str) -> List[Dict[str, Any]]:
        """Extract keywords from content"""
        # Clean and tokenize content
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Remove stop words
        filtered_words = [word for word in words if word not in self.stop_words]
        
        # Count word frequency
        word_freq = Counter(filtered_words)
        
        # Return top keywords with frequency
        keywords = []
        for word, freq in word_freq.most_common(20):
            keywords.append({
                'keyword': word,
                'frequency': freq,
                'density': round((freq / len(words)) * 100, 2) if words else 0
            })
        
        return keywords
    
    def _calculate_readability(self, content: str, word_count: int, sentence_count: int) -> float:
        """Calculate simplified readability score"""
        if sentence_count == 0 or word_count == 0:
            return 0
        
        # Count syllables (simplified)
        syllable_count = 0
        for word in content.split():
            syllable_count += max(1, len(re.findall(r'[aeiouAEIOU]', word)))
        
        # Simplified Flesch Reading Ease formula
        avg_sentence_length = word_count / sentence_count
        avg_syllables_per_word = syllable_count / word_count
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        return max(0, min(100, round(score, 1)))
    
    def _calculate_seo_score(self, word_count: int, keyword_density: Dict, 
                           readability_score: float, content: str) -> Dict[str, Any]:
        """Calculate overall SEO score"""
        score = 0
        max_score = 100
        factors = []
        
        # Word count factor (20 points)
        if 300 <= word_count <= 2000:
            word_score = 20
            factors.append("Good content length")
        elif word_count < 300:
            word_score = max(0, (word_count / 300) * 20)
            factors.append("Content too short")
        else:
            word_score = max(10, 20 - ((word_count - 2000) / 1000) * 5)
            factors.append("Content might be too long")
        
        score += word_score
        
        # Keyword density factor (30 points)
        if keyword_density:
            avg_density = sum(kw['density'] for kw in keyword_density.values()) / len(keyword_density)
            if 1 <= avg_density <= 3:
                keyword_score = 30
                factors.append("Good keyword density")
            elif avg_density < 1:
                keyword_score = avg_density * 30
                factors.append("Low keyword density")
            else:
                keyword_score = max(10, 30 - (avg_density - 3) * 5)
                factors.append("High keyword density")
        else:
            keyword_score = 0
            factors.append("No target keywords analyzed")
        
        score += keyword_score
        
        # Readability factor (25 points)
        if readability_score >= 60:
            readability_points = 25
            factors.append("Good readability")
        elif readability_score >= 30:
            readability_points = (readability_score - 30) / 30 * 25
            factors.append("Moderate readability")
        else:
            readability_points = readability_score / 30 * 15
            factors.append("Poor readability")
        
        score += readability_points
        
        # Structure factor (25 points)
        structure_score = 0
        if len(content.split('\n\n')) > 1:
            structure_score += 10
            factors.append("Has paragraphs")
        if re.search(r'#+ ', content):
            structure_score += 10
            factors.append("Has headings")
        if len(re.findall(r'[.!?]', content)) > 3:
            structure_score += 5
            factors.append("Good sentence variety")
        
        score += structure_score
        
        return {
            'total_score': round(score, 1),
            'max_score': max_score,
            'percentage': round((score / max_score) * 100, 1),
            'grade': self._get_seo_grade(score),
            'factors': factors
        }
    
    def _get_seo_grade(self, score: float) -> str:
        """Get SEO grade based on score"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    def _generate_seo_recommendations(self, word_count: int, keyword_density: Dict,
                                    readability_score: float, content: str) -> List[str]:
        """Generate SEO improvement recommendations"""
        recommendations = []
        
        if word_count < 300:
            recommendations.append("Increase content length to at least 300 words")
        elif word_count > 2000:
            recommendations.append("Consider breaking content into multiple pieces")
        
        if keyword_density:
            avg_density = sum(kw['density'] for kw in keyword_density.values()) / len(keyword_density)
            if avg_density < 1:
                recommendations.append("Increase keyword density (aim for 1-3%)")
            elif avg_density > 3:
                recommendations.append("Reduce keyword density to avoid keyword stuffing")
        
        if readability_score < 60:
            recommendations.append("Improve readability with shorter sentences and simpler words")
        
        if not re.search(r'#+ ', content):
            recommendations.append("Add headings to improve content structure")
        
        if len(content.split('\n\n')) <= 1:
            recommendations.append("Break content into multiple paragraphs")
        
        return recommendations
    
    def _generate_fallback_meta_tags(self, content: str, title: str = None) -> Dict[str, Any]:
        """Generate fallback meta tags when AI fails"""
        # Extract first sentence for description
        sentences = re.split(r'[.!?]+', content)
        description = sentences[0][:160] if sentences else content[:160]
        
        # Extract keywords
        keywords = [kw['keyword'] for kw in self._extract_keywords(content)[:5]]
        
        return {
            'success': True,
            'meta_tags': {
                'meta_title': (title or 'Untitled')[:60],
                'meta_description': description,
                'keywords': keywords,
                'og_title': (title or 'Untitled')[:60],
                'og_description': description
            }
        }
    
    def _calculate_improvements(self, original: Dict, optimized: Dict) -> List[str]:
        """Calculate improvements between original and optimized content"""
        improvements = []
        
        if not original.get('success') or not optimized.get('success'):
            return improvements
        
        orig_score = original.get('seo_score', {}).get('total_score', 0)
        opt_score = optimized.get('seo_score', {}).get('total_score', 0)
        
        if opt_score > orig_score:
            improvements.append(f"SEO score improved by {round(opt_score - orig_score, 1)} points")
        
        orig_readability = original.get('metrics', {}).get('readability_score', 0)
        opt_readability = optimized.get('metrics', {}).get('readability_score', 0)
        
        if opt_readability > orig_readability:
            improvements.append(f"Readability improved by {round(opt_readability - orig_readability, 1)} points")
        
        # Check keyword density improvements
        orig_keywords = original.get('keywords', {}).get('target_analysis', {})
        opt_keywords = optimized.get('keywords', {}).get('target_analysis', {})
        
        for keyword in orig_keywords:
            if keyword in opt_keywords:
                orig_density = orig_keywords[keyword]['density']
                opt_density = opt_keywords[keyword]['density']
                if opt_density > orig_density:
                    improvements.append(f"'{keyword}' keyword density improved")
        
        return improvements

# Singleton instance
seo_service = SEOService()

