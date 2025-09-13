-- SocialHub Database Schema
-- This file contains the complete database schema for the SocialHub application

-- Enable UUID extension for PostgreSQL
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    avatar_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Social accounts table
CREATE TABLE IF NOT EXISTS social_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    platform_user_id VARCHAR(255) NOT NULL,
    username VARCHAR(255),
    display_name VARCHAR(255),
    avatar_url VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    followers_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    posts_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, platform, platform_user_id)
);

-- Posts table
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    media_urls TEXT[], -- Array of media URLs
    hashtags TEXT[], -- Array of hashtags
    mentions TEXT[], -- Array of mentions
    status VARCHAR(20) DEFAULT 'draft', -- draft, scheduled, published, failed
    scheduled_time TIMESTAMP,
    published_at TIMESTAMP,
    is_thread BOOLEAN DEFAULT FALSE,
    thread_parent_id INTEGER REFERENCES posts(id),
    thread_order INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Post platforms table (many-to-many relationship)
CREATE TABLE IF NOT EXISTS post_platforms (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending', -- pending, published, failed
    error_message TEXT,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, platform)
);

-- Analytics table
CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    social_account_id INTEGER REFERENCES social_accounts(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- reach, impressions, likes, shares, comments, clicks, etc.
    metric_value INTEGER NOT NULL DEFAULT 0,
    date_recorded DATE NOT NULL,
    hour_recorded INTEGER, -- 0-23 for hourly analytics
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX(user_id, platform, date_recorded),
    INDEX(post_id, metric_type),
    UNIQUE(user_id, post_id, platform, metric_type, date_recorded, hour_recorded)
);

-- Content templates table
CREATE TABLE IF NOT EXISTS content_templates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[], -- Array of tags
    is_public BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scheduled tasks table
CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_type VARCHAR(50) NOT NULL, -- post_publish, analytics_sync, etc.
    task_data JSONB NOT NULL,
    scheduled_time TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    error_message TEXT,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX(scheduled_time, status)
);

-- User settings table
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    setting_key VARCHAR(100) NOT NULL,
    setting_value JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, setting_key)
);

-- API usage tracking table
CREATE TABLE IF NOT EXISTS api_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX(user_id, created_at),
    INDEX(endpoint, created_at)
);

-- Webhooks table
CREATE TABLE IF NOT EXISTS webhooks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    webhook_url VARCHAR(500) NOT NULL,
    secret_key VARCHAR(255),
    events TEXT[] NOT NULL, -- Array of event types
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX(user_id, created_at),
    INDEX(action, created_at)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

CREATE INDEX IF NOT EXISTS idx_social_accounts_user_id ON social_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_social_accounts_platform ON social_accounts(platform);
CREATE INDEX IF NOT EXISTS idx_social_accounts_is_active ON social_accounts(is_active);

CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_scheduled_time ON posts(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_posts_published_at ON posts(published_at);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at);

CREATE INDEX IF NOT EXISTS idx_post_platforms_post_id ON post_platforms(post_id);
CREATE INDEX IF NOT EXISTS idx_post_platforms_platform ON post_platforms(platform);
CREATE INDEX IF NOT EXISTS idx_post_platforms_status ON post_platforms(status);

CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_post_id ON analytics(post_id);
CREATE INDEX IF NOT EXISTS idx_analytics_platform ON analytics(platform);
CREATE INDEX IF NOT EXISTS idx_analytics_date_recorded ON analytics(date_recorded);
CREATE INDEX IF NOT EXISTS idx_analytics_metric_type ON analytics(metric_type);

CREATE INDEX IF NOT EXISTS idx_content_templates_user_id ON content_templates(user_id);
CREATE INDEX IF NOT EXISTS idx_content_templates_category ON content_templates(category);
CREATE INDEX IF NOT EXISTS idx_content_templates_is_public ON content_templates(is_public);

CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_user_id ON scheduled_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_scheduled_time ON scheduled_tasks(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_status ON scheduled_tasks(status);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_social_accounts_updated_at BEFORE UPDATE ON social_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_templates_updated_at BEFORE UPDATE ON content_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_webhooks_updated_at BEFORE UPDATE ON webhooks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default user settings
INSERT INTO user_settings (user_id, setting_key, setting_value) 
SELECT id, 'notifications', '{"email": true, "push": true, "sms": false}'::jsonb
FROM users
WHERE NOT EXISTS (
    SELECT 1 FROM user_settings 
    WHERE user_settings.user_id = users.id 
    AND setting_key = 'notifications'
);

-- Insert default analytics metrics for tracking
INSERT INTO analytics (user_id, platform, metric_type, metric_value, date_recorded)
SELECT DISTINCT sa.user_id, sa.platform, 'followers', sa.followers_count, CURRENT_DATE
FROM social_accounts sa
WHERE sa.is_active = true
AND NOT EXISTS (
    SELECT 1 FROM analytics a
    WHERE a.user_id = sa.user_id
    AND a.platform = sa.platform
    AND a.metric_type = 'followers'
    AND a.date_recorded = CURRENT_DATE
);

-- Create views for common queries
CREATE OR REPLACE VIEW user_analytics_summary AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(DISTINCT sa.id) as connected_accounts,
    COUNT(DISTINCT p.id) as total_posts,
    COUNT(DISTINCT CASE WHEN p.status = 'published' THEN p.id END) as published_posts,
    COUNT(DISTINCT CASE WHEN p.scheduled_time > CURRENT_TIMESTAMP THEN p.id END) as scheduled_posts,
    COALESCE(SUM(CASE WHEN a.metric_type = 'followers' THEN a.metric_value END), 0) as total_followers,
    COALESCE(SUM(CASE WHEN a.metric_type = 'likes' THEN a.metric_value END), 0) as total_likes,
    COALESCE(SUM(CASE WHEN a.metric_type = 'shares' THEN a.metric_value END), 0) as total_shares
FROM users u
LEFT JOIN social_accounts sa ON u.id = sa.user_id AND sa.is_active = true
LEFT JOIN posts p ON u.id = p.user_id
LEFT JOIN analytics a ON u.id = a.user_id AND a.date_recorded >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY u.id, u.username;

CREATE OR REPLACE VIEW platform_performance AS
SELECT 
    sa.platform,
    COUNT(DISTINCT sa.user_id) as active_users,
    SUM(sa.followers_count) as total_followers,
    COUNT(DISTINCT p.id) as total_posts,
    AVG(CASE WHEN a.metric_type = 'engagement_rate' THEN a.metric_value END) as avg_engagement_rate
FROM social_accounts sa
LEFT JOIN posts p ON sa.user_id = p.user_id
LEFT JOIN post_platforms pp ON p.id = pp.post_id AND pp.platform = sa.platform
LEFT JOIN analytics a ON sa.id = a.social_account_id AND a.date_recorded >= CURRENT_DATE - INTERVAL '30 days'
WHERE sa.is_active = true
GROUP BY sa.platform;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO socialhub_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO socialhub_user;
-- GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO socialhub_user;

