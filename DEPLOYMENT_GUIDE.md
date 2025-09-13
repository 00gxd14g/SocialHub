# SocialHub - Deployment Guide

## 🚀 Deployment Options

SocialHub can be deployed in multiple ways depending on your needs and infrastructure preferences. This guide covers all major deployment scenarios.

## 📋 Pre-Deployment Checklist

### ✅ Required Preparations
- [ ] All environment variables configured
- [ ] Database setup completed
- [ ] API keys obtained and tested
- [ ] Frontend built for production
- [ ] SSL certificates ready (for HTTPS)
- [ ] Domain name configured (if applicable)

### ✅ Security Checklist
- [ ] Change default JWT secret key
- [ ] Enable HTTPS in production
- [ ] Configure CORS properly
- [ ] Set up proper firewall rules
- [ ] Enable rate limiting
- [ ] Configure secure headers

## 🖥 Option 1: Single Server Deployment (Recommended for Small-Medium Scale)

This is the simplest deployment option where both frontend and backend run on the same server.

### Step 1: Server Setup

#### Ubuntu/Debian Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv nginx supervisor -y

# Install Node.js (for building frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### CentOS/RHEL Server
```bash
# Update system
sudo yum update -y

# Install required packages
sudo yum install python3 python3-pip nginx supervisor -y

# Install Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs
```

### Step 2: Deploy Application

```bash
# Create application directory
sudo mkdir -p /var/www/socialhub
sudo chown $USER:$USER /var/www/socialhub

# Upload and extract project files
cd /var/www/socialhub
# Upload your SocialHub_Complete_Project.zip here
unzip SocialHub_Complete_Project.zip
cd SocialHub_Complete_Project

# Set up backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Build frontend (if not already built)
cd ../frontend
npm install
npm run build

# Copy built files to backend static directory
cp -r dist/* ../backend/src/static/
```

### Step 3: Configure Environment

```bash
# Create production environment file
cd /var/www/socialhub/SocialHub_Complete_Project/backend
cat > .env << EOF
FLASK_ENV=production
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_BASE=https://api.openai.com/v1
JWT_SECRET_KEY=your-super-secure-jwt-secret-key
DATABASE_URL=sqlite:///production.db

# Social Media API Keys
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
EOF
```

### Step 4: Configure Supervisor (Process Management)

```bash
# Create supervisor configuration
sudo cat > /etc/supervisor/conf.d/socialhub.conf << EOF
[program:socialhub]
command=/var/www/socialhub/SocialHub_Complete_Project/backend/venv/bin/python src/main.py
directory=/var/www/socialhub/SocialHub_Complete_Project/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/socialhub.log
environment=PATH="/var/www/socialhub/SocialHub_Complete_Project/backend/venv/bin"
EOF

# Start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start socialhub
```

### Step 5: Configure Nginx (Reverse Proxy)

```bash
# Create Nginx configuration
sudo cat > /etc/nginx/sites-available/socialhub << EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files (optional optimization)
    location /static/ {
        alias /var/www/socialhub/SocialHub_Complete_Project/backend/src/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/socialhub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: SSL Setup with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (already set up by certbot)
sudo crontab -l | grep certbot
```

## ☁️ Option 2: Cloud Platform Deployment

### Heroku Deployment

#### Step 1: Prepare for Heroku
```bash
# Create Procfile in backend directory
cd backend
echo "web: python src/main.py" > Procfile

# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Update requirements.txt with gunicorn
echo "gunicorn==20.1.0" >> requirements.txt
```

#### Step 2: Modify main.py for Heroku
```python
# Add to the end of src/main.py
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

#### Step 3: Deploy to Heroku
```bash
# Install Heroku CLI and login
heroku login

# Create Heroku app
heroku create your-socialhub-app

# Set environment variables
heroku config:set OPENAI_API_KEY=your-key
heroku config:set JWT_SECRET_KEY=your-secret

# Deploy
git init
git add .
git commit -m "Initial deployment"
heroku git:remote -a your-socialhub-app
git push heroku main
```

### DigitalOcean App Platform

#### Step 1: Create app.yaml
```yaml
name: socialhub
services:
- name: backend
  source_dir: /backend
  github:
    repo: your-username/socialhub
    branch: main
  run_command: python src/main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: OPENAI_API_KEY
    value: your-openai-api-key
    type: SECRET
  - key: JWT_SECRET_KEY
    value: your-jwt-secret
    type: SECRET
```

#### Step 2: Deploy
```bash
# Install doctl CLI
# Create app
doctl apps create app.yaml
```

### AWS Elastic Beanstalk

#### Step 1: Prepare application
```bash
# Create application.py (EB entry point)
cd backend
cat > application.py << EOF
from src.main import app

if __name__ == "__main__":
    app.run()
EOF
```

#### Step 2: Deploy
```bash
# Install EB CLI
pip install awsebcli

# Initialize and deploy
eb init
eb create socialhub-prod
eb deploy
```

## 🐳 Option 3: Docker Deployment

### Step 1: Create Dockerfiles

#### Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "src/main.py"]
```

#### Frontend Dockerfile (if deploying separately)
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Step 2: Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DATABASE_URL=postgresql://postgres:password@db:5432/socialhub
    depends_on:
      - db
    volumes:
      - ./backend:/app

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=socialhub
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Step 3: Deploy with Docker
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Scale backend
docker-compose up -d --scale backend=3
```

## 🌐 Option 4: Kubernetes Deployment

### Step 1: Create Kubernetes Manifests

#### Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: socialhub-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: socialhub-backend
  template:
    metadata:
      labels:
        app: socialhub-backend
    spec:
      containers:
      - name: backend
        image: your-registry/socialhub-backend:latest
        ports:
        - containerPort: 5000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: socialhub-secrets
              key: openai-api-key
```

#### Service
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: socialhub-service
spec:
  selector:
    app: socialhub-backend
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

### Step 2: Deploy to Kubernetes
```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods
kubectl get services
```

## 🗄 Database Deployment Options

### PostgreSQL (Recommended for Production)

#### Local PostgreSQL
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE socialhub;
CREATE USER socialhub_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE socialhub TO socialhub_user;
```

#### Managed PostgreSQL (AWS RDS, DigitalOcean, etc.)
```bash
# Update environment variable
DATABASE_URL=postgresql://username:password@host:port/database
```

### Redis (for Caching and Sessions)
```bash
# Install Redis
sudo apt install redis-server

# Configure in application
REDIS_URL=redis://localhost:6379/0
```

## 🔧 Production Optimizations

### Performance Optimizations

#### Gunicorn Configuration
```python
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
```

#### Nginx Optimizations
```nginx
# nginx.conf optimizations
worker_processes auto;
worker_connections 1024;

http {
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript;

    # Caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Security Hardening

#### Environment Variables
```bash
# Use strong secrets
JWT_SECRET_KEY=$(openssl rand -base64 32)
DATABASE_PASSWORD=$(openssl rand -base64 32)
```

#### Firewall Configuration
```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

#### SSL/TLS Configuration
```nginx
# Strong SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
add_header Strict-Transport-Security "max-age=63072000" always;
```

## 📊 Monitoring and Logging

### Application Monitoring
```python
# Add to main.py
import logging
from flask import request
import time

@app.before_request
def log_request_info():
    app.logger.info('Request: %s %s', request.method, request.url)

@app.after_request
def log_response_info(response):
    app.logger.info('Response: %s', response.status_code)
    return response
```

### System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Set up log rotation
sudo cat > /etc/logrotate.d/socialhub << EOF
/var/log/socialhub.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
EOF
```

## 🔄 Backup and Recovery

### Database Backup
```bash
# PostgreSQL backup script
#!/bin/bash
BACKUP_DIR="/var/backups/socialhub"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -h localhost -U socialhub_user socialhub > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

### Application Backup
```bash
# Backup application files
tar -czf /var/backups/socialhub_app_$(date +%Y%m%d).tar.gz /var/www/socialhub
```

## 🚨 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
sudo supervisorctl tail socialhub
sudo journalctl -u nginx

# Check process
ps aux | grep python
netstat -tlnp | grep 5000
```

#### Database Connection Issues
```bash
# Test database connection
python -c "
import os
from sqlalchemy import create_engine
engine = create_engine(os.getenv('DATABASE_URL'))
print('Database connection successful')
"
```

#### SSL Certificate Issues
```bash
# Check certificate
sudo certbot certificates

# Renew certificate
sudo certbot renew --dry-run
```

### Performance Issues
```bash
# Monitor resources
htop
iotop
df -h

# Check application performance
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:5000"
```

## 📞 Support and Maintenance

### Regular Maintenance Tasks
- [ ] Update system packages monthly
- [ ] Rotate logs weekly
- [ ] Backup database daily
- [ ] Monitor disk space
- [ ] Check SSL certificate expiry
- [ ] Update application dependencies

### Health Checks
```bash
# Create health check script
#!/bin/bash
curl -f http://localhost:5000/api/health || exit 1
```

This comprehensive deployment guide covers all major deployment scenarios. Choose the option that best fits your infrastructure needs and scale requirements.

