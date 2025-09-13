# SocialHub - Installation Guide

## 📋 Prerequisites

Before installing SocialHub, ensure you have the following installed on your system:

### Required Software
- **Python 3.11 or higher**
- **Node.js 18 or higher**
- **npm or pnpm** (pnpm recommended for faster installs)
- **Git** (for version control)

### API Keys (Optional but Recommended)
- **OpenAI API Key** - For AI content generation features
- **Social Media API Keys** - For full platform integration:
  - Facebook Graph API
  - Twitter API v2
  - LinkedIn API
  - Instagram Basic Display API

## 🚀 Installation Steps

### Step 1: Extract Project Files
Extract the SocialHub project files to your desired directory:
```bash
# Extract the zip file to your preferred location
unzip SocialHub_Complete_Project.zip
cd SocialHub_Complete_Project
```

### Step 2: Backend Setup

#### 2.1 Navigate to Backend Directory
```bash
cd backend
```

#### 2.2 Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 2.3 Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 2.4 Set Environment Variables
Create a `.env` file in the backend directory:
```bash
# Create .env file
touch .env
```

Add the following content to `.env`:
```env
# OpenAI Configuration (Required for AI features)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Database Configuration (Optional - defaults to SQLite)
DATABASE_URL=sqlite:///socialhub.db

# Social Media API Keys (Optional)
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
INSTAGRAM_APP_ID=your-instagram-app-id
INSTAGRAM_APP_SECRET=your-instagram-app-secret
```

#### 2.5 Initialize Database
```bash
# The database will be automatically created when you first run the application
python src/main.py
```

### Step 3: Frontend Setup (Development Mode)

If you want to run the frontend in development mode:

#### 3.1 Navigate to Frontend Directory
```bash
cd ../frontend
```

#### 3.2 Install Node.js Dependencies
```bash
# Using pnpm (recommended)
pnpm install

# Or using npm
npm install
```

#### 3.3 Start Development Server
```bash
# Using pnpm
pnpm run dev

# Or using npm
npm run dev
```

### Step 4: Production Setup

For production deployment, the frontend is already built and included in the backend:

#### 4.1 Start Backend Server
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python src/main.py
```

#### 4.2 Access Application
Open your browser and navigate to:
```
http://localhost:5000
```

## 🔧 Configuration Options

### Database Configuration

#### SQLite (Default)
No additional configuration needed. The database file will be created automatically.

#### PostgreSQL (Production Recommended)
1. Install PostgreSQL
2. Create a database
3. Update the `DATABASE_URL` in your `.env` file:
```env
DATABASE_URL=postgresql://username:password@localhost/socialhub
```

#### MySQL
1. Install MySQL
2. Create a database
3. Update the `DATABASE_URL` in your `.env` file:
```env
DATABASE_URL=mysql://username:password@localhost/socialhub
```

### Social Media API Setup

#### Facebook Graph API
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Facebook Login and Pages API products
4. Get your App ID and App Secret
5. Add to `.env` file

#### Twitter API v2
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new project and app
3. Generate API keys and tokens
4. Add to `.env` file

#### LinkedIn API
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Create a new app
3. Request access to LinkedIn API
4. Get your Client ID and Client Secret
5. Add to `.env` file

#### Instagram Basic Display API
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Instagram Basic Display product
4. Get your App ID and App Secret
5. Add to `.env` file

## 🐳 Docker Installation (Alternative)

If you prefer using Docker:

### Step 1: Build Docker Images
```bash
# Build backend image
cd backend
docker build -t socialhub-backend .

# Build frontend image (if running separately)
cd ../frontend
docker build -t socialhub-frontend .
```

### Step 2: Run with Docker Compose
```bash
# From project root
docker-compose up -d
```

## 🧪 Testing Installation

### Test Backend API
```bash
# Test if backend is running
curl http://localhost:5000/api/health

# Expected response: {"status": "healthy"}
```

### Test Frontend
1. Open browser to `http://localhost:5000`
2. You should see the SocialHub login page
3. Try creating a test account and logging in

### Test AI Features
1. Log in to the application
2. Go to "Create Post" page
3. Click the AI content generator
4. Enter a topic and generate content
5. Verify AI-generated content appears

## 🔍 Troubleshooting

### Common Issues

#### Python Virtual Environment Issues
```bash
# If virtual environment activation fails
python -m pip install --user virtualenv
python -m virtualenv venv
```

#### Node.js Dependency Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules
npm install
```

#### Database Connection Issues
```bash
# Check if database file exists
ls -la backend/src/database/

# Reset database (WARNING: This will delete all data)
rm backend/src/database/app.db
python backend/src/main.py
```

#### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill process (replace PID with actual process ID)
kill -9 PID

# Or use different port
export FLASK_RUN_PORT=5001
python src/main.py
```

### Environment Variable Issues
```bash
# Check if environment variables are loaded
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"

# If None, ensure .env file is in correct location and properly formatted
```

### OpenAI API Issues
- Verify your API key is valid
- Check your OpenAI account has sufficient credits
- Ensure API key has proper permissions

## 📚 Additional Resources

### Development Tools
- **VS Code Extensions**: Python, ES

