# SocialHub API Documentation

## 📋 Overview

The SocialHub API is a RESTful API that provides comprehensive social media management capabilities. All API endpoints return JSON responses and use standard HTTP status codes.

**Base URL**: `http://localhost:5000/api`

## 🔐 Authentication

SocialHub uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Authentication Flow
1. Register or login to get a JWT token
2. Include the token in subsequent requests
3. Refresh the token when it expires

## 📚 API Endpoints

### 🔑 Authentication Endpoints

#### Register User
```http
POST /api/auth/register
```

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

#### Login User
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

#### Refresh Token
```http
POST /api/auth/refresh
```

**Headers:**
```
Authorization: Bearer <refresh-token>
```

**Response:**
```json
{
  "access_token": "new-jwt-token"
}
```

### 📝 Posts Management

#### Get User Posts
```http
GET /api/posts
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Posts per page (default: 10)
- `status` (optional): Filter by status (draft, scheduled, published)

**Response:**
```json
{
  "posts": [
    {
      "id": 1,
      "content": "Hello world!",
      "platforms": ["twitter", "facebook"],
      "status": "published",
      "scheduled_time": null,
      "created_at": "2024-01-01T12:00:00Z",
      "analytics": {
        "views": 1250,
        "likes": 45,
        "shares": 12
      }
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 5,
    "per_page": 10,
    "total": 50
  }
}
```

#### Create Post
```http
POST /api/posts
```

**Request Body:**
```json
{
  "content": "string",
  "platforms": ["twitter", "facebook", "instagram", "linkedin"],
  "media_urls": ["string"],
  "scheduled_time": "2024-01-01T12:00:00Z",
  "tags": ["string"]
}
```

**Response:**
```json
{
  "message": "Post created successfully",
  "post": {
    "id": 1,
    "content": "Hello world!",
    "platforms": ["twitter", "facebook"],
    "status": "scheduled",
    "scheduled_time": "2024-01-01T12:00:00Z"
  }
}
```

#### Update Post
```http
PUT /api/posts/{post_id}
```

**Request Body:**
```json
{
  "content": "string",
  "platforms": ["string"],
  "scheduled_time": "2024-01-01T12:00:00Z"
}
```

#### Delete Post
```http
DELETE /api/posts/{post_id}
```

**Response:**
```json
{
  "message": "Post deleted successfully"
}
```

#### Schedule Post
```http
POST /api/posts/{post_id}/schedule
```

**Request Body:**
```json
{
  "scheduled_time": "2024-01-01T12:00:00Z"
}
```

### 🔗 Social Accounts Management

#### Get Connected Accounts
```http
GET /api/social-accounts
```

**Response:**
```json
{
  "accounts": [
    {
      "id": 1,
      "platform": "twitter",
      "username": "@john_doe",
      "display_name": "John Doe",
      "followers_count": 1250,
      "is_active": true,
      "connected_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

#### Connect Social Account
```http
POST /api/social-accounts/connect
```

**Request Body:**
```json
{
  "platform": "twitter",
  "access_token": "string",
  "access_token_secret": "string",
  "username": "string"
}
```

#### Disconnect Account
```http
DELETE /api/social-accounts/{account_id}
```

**Response:**
```json
{
  "message": "Account disconnected successfully"
}
```

### 📊 Analytics Endpoints

#### Get Analytics Overview
```http
GET /api/analytics/overview
```

**Query Parameters:**
- `period` (optional): Time period (7d, 30d, 90d, 1y)
- `platforms` (optional): Comma-separated platform names

**Response:**
```json
{
  "overview": {
    "total_reach": 12456,
    "total_engagement": 3210,
    "follower_growth": 567,
    "engagement_rate": 8.5,
    "period": "30d"
  },
  "platform_breakdown": {
    "twitter": {
      "reach": 5000,
      "engagement": 1200,
      "followers": 1250
    },
    "facebook": {
      "reach": 4000,
      "engagement": 1000,
      "followers": 2100
    }
  },
  "engagement_over_time": [
    {
      "date": "2024-01-01",
      "engagement": 250
    }
  ]
}
```

#### Get Platform Analytics
```http
GET /api/analytics/platform/{platform}
```

**Response:**
```json
{
  "platform": "twitter",
  "metrics": {
    "followers": 1250,
    "following": 500,
    "posts_count": 45,
    "engagement_rate": 8.5
  },
  "recent_posts": [
    {
      "id": 1,
      "content": "Hello world!",
      "engagement": {
        "likes": 45,
        "retweets": 12,
        "replies": 8
      }
    }
  ]
}
```

#### Get Top Performing Posts
```http
GET /api/analytics/posts/top-performing
```

**Query Parameters:**
- `limit` (optional): Number of posts to return (default: 10)
- `period` (optional): Time period (7d, 30d, 90d)

**Response:**
```json
{
  "posts": [
    {
      "id": 1,
      "content": "Amazing product launch!",
      "platform": "twitter",
      "engagement_score": 95.5,
      "metrics": {
        "likes": 450,
        "shares": 120,
        "comments": 80
      }
    }
  ]
}
```

#### Export Analytics
```http
POST /api/analytics/export
```

**Request Body:**
```json
{
  "format": "csv",
  "period": "30d",
  "platforms": ["twitter", "facebook"],
  "metrics": ["reach", "engagement", "followers"]
}
```

**Response:**
```json
{
  "download_url": "https://api.socialhub.com/exports/analytics_2024-01-01.csv",
  "expires_at": "2024-01-01T12:00:00Z"
}
```

### 🤖 AI Content Generation

#### Generate Post Content
```http
POST /api/ai/generate-post
```

**Request Body:**
```json
{
  "topic": "string",
  "platform": "twitter",
  "tone": "professional",
  "length": "medium",
  "target_audience": "business professionals",
  "keywords": ["string"]
}
```

**Response:**
```json
{
  "success": true,
  "generated_content": {
    "content": "🚀 Exciting news about AI in marketing...",
    "hashtags": ["#AI", "#Marketing", "#Innovation"],
    "character_count": 195,
    "sentiment": "positive",
    "engagement_prediction": 8.5
  }
}
```

#### Generate Hashtags
```http
POST /api/ai/generate-hashtags
```

**Request Body:**
```json
{
  "content": "string",
  "platform": "instagram",
  "count": 10
}
```

**Response:**
```json
{
  "success": true,
  "hashtags": [
    {
      "tag": "#SocialMedia",
      "relevance_score": 9.5,
      "popularity": "high"
    }
  ]
}
```

#### Optimize Content for SEO
```http
POST /api/ai/optimize-seo
```

**Request Body:**
```json
{
  "content": "string",
  "target_keywords": ["string"],
  "platform": "blog"
}
```

**Response:**
```json
{
  "success": true,
  "optimized_content": "string",
  "seo_score": 85,
  "improvements": [
    "Added target keyword in title",
    "Improved meta description"
  ]
}
```

#### Analyze Content Sentiment
```http
POST /api/ai/analyze-sentiment
```

**Request Body:**
```json
{
  "content": "string"
}
```

**Response:**
```json
{
  "success": true,
  "sentiment": {
    "overall": "positive",
    "confidence": 0.95,
    "emotions": {
      "joy": 0.8,
      "excitement": 0.7,
      "trust": 0.6
    }
  }
}
```

#### Generate Blog Post
```http
POST /api/ai/generate-blog
```

**Request Body:**
```json
{
  "topic": "string",
  "target_audience": "string",
  "word_count": 1000,
  "tone": "professional",
  "include_seo": true
}
```

**Response:**
```json
{
  "success": true,
  "blog_post": {
    "title": "string",
    "content": "string",
    "meta_description": "string",
    "tags": ["string"],
    "estimated_read_time": 5
  }
}
```

### 🔍 SEO Tools

#### Analyze Content SEO
```http
POST /api/seo/analyze
```

**Request Body:**
```json
{
  "content": "string",
  "target_keywords": ["string"]
}
```

**Response:**
```json
{
  "success": true,
  "seo_score": {
    "overall": 85,
    "breakdown": {
      "keyword_density": 90,
      "readability": 80,
      "content_length": 85,
      "structure": 90
    }
  },
  "recommendations": [
    "Add more internal links",
    "Improve meta description"
  ]
}
```

#### Generate Meta Tags
```http
POST /api/seo/meta-tags
```

**Request Body:**
```json
{
  "content": "string",
  "title": "string"
}
```

**Response:**
```json
{
  "success": true,
  "meta_tags": {
    "title": "string",
    "description": "string",
    "keywords": "string",
    "og_title": "string",
    "og_description": "string",
    "twitter_title": "string",
    "twitter_description": "string"
  }
}
```

#### Optimize Content
```http
POST /api/seo/optimize
```

**Request Body:**
```json
{
  "content": "string",
  "target_keywords": ["string"]
}
```

**Response:**
```json
{
  "success": true,
  "optimized_content": "string",
  "changes_made": [
    "Added target keyword in first paragraph",
    "Improved heading structure"
  ]
}
```

#### Generate Schema Markup
```http
POST /api/seo/schema-markup
```

**Request Body:**
```json
{
  "content_type": "article",
  "data": {
    "title": "string",
    "author": "string",
    "date_published": "2024-01-01",
    "description": "string"
  }
}
```

**Response:**
```json
{
  "success": true,
  "schema_markup": {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "string",
    "author": {
      "@type": "Person",
      "name": "string"
    }
  }
}
```

## 📊 Response Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request |
| 401  | Unauthorized |
| 403  | Forbidden |
| 404  | Not Found |
| 422  | Validation Error |
| 500  | Internal Server Error |

## 🔄 Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Authentication endpoints**: 5 requests per minute
- **Content generation**: 10 requests per minute
- **Analytics**: 100 requests per minute
- **Other endpoints**: 60 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200
```

## 🛠 Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request data is invalid",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

## 📝 Examples

### Complete Post Creation Flow

```javascript
// 1. Login
const loginResponse = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});
const { access_token } = await loginResponse.json();

// 2. Generate AI content
const contentResponse = await fetch('/api/ai/generate-post', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    topic: 'Social Media Marketing',
    platform: 'twitter',
    tone: 'professional'
  })
});
const { generated_content } = await contentResponse.json();

// 3. Create post
const postResponse = await fetch('/api/posts', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    content: generated_content.content,
    platforms: ['twitter', 'facebook'],
    scheduled_time: '2024-01-01T12:00:00Z'
  })
});
```

## 🔧 SDK and Libraries

### JavaScript/Node.js
```javascript
import SocialHubAPI from 'socialhub-api-client';

const client = new SocialHubAPI({
  baseURL: 'http://localhost:5000/api',
  apiKey: 'your-api-key'
});

// Generate content
const content = await client.ai.generatePost({
  topic: 'AI in Marketing',
  platform: 'twitter'
});

// Create post
const post = await client.posts.create({
  content: content.content,
  platforms: ['twitter', 'facebook']
});
```

### Python
```python
from socialhub_client import SocialHubClient

client = SocialHubClient(
    base_url='http://localhost:5000/api',
    api_key='your-api-key'
)

# Generate content
content = client.ai.generate_post(
    topic='AI in Marketing',
    platform='twitter'
)

# Create post
post = client.posts.create(
    content=content['content'],
    platforms=['twitter', 'facebook']
)
```

## 📚 Additional Resources

- **Postman Collection**: Import the provided Postman collection for easy API testing
- **OpenAPI Specification**: Available at `/api/docs` when running the server
- **Webhook Documentation**: See webhook setup guide for real-time notifications
- **Rate Limiting**: Detailed rate limiting policies and best practices

