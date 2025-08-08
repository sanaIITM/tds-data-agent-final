# TDS Data Analyst Agent - Deployment Guide

## 🚀 Deploy to Render (Recommended)

### Prerequisites
1. GitHub account
2. Render account (free tier available)
3. AI Pipe API key

### Step-by-Step Deployment

#### 1. Push to GitHub
```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial commit: TDS Data Analyst Agent"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/tds-data-analyst-agent.git
git branch -M main
git push -u origin main
```

#### 2. Deploy on Render
1. Go to [render.com](https://render.com) and sign in
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

**Basic Settings:**
- **Name**: `tds-data-analyst-agent`
- **Environment**: `Python 3`
- **Region**: Choose closest to your location
- **Branch**: `main`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python run.py`

**Environment Variables:**
- **OPENAI_API_KEY**: `eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDA4MjNAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.woV2mROOCp5wS4qB4Hc0P86xw_zZibv2Vnvic0EcWYA`
- **OPENAI_BASE_URL**: `https://aipipe.org/openai/v1`

5. Click "Create Web Service"

#### 3. Verify Deployment
Once deployed, your API will be available at:
```
https://tds-data-analyst-agent.onrender.com
```

Test the health endpoint:
```bash
curl https://tds-data-analyst-agent.onrender.com/
```

Test the main API:
```bash
curl -X POST "https://tds-data-analyst-agent.onrender.com/api/" \
  -F "files=@questions.txt" \
  -F "files=@data.csv"
```

### 🔧 Alternative Deployment Options

#### Railway
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Set environment variables
4. Deploy automatically

#### Heroku
1. Install Heroku CLI
2. Create `Procfile`:
```
web: python run.py
```
3. Deploy:
```bash
heroku create tds-data-analyst-agent
heroku config:set OPENAI_API_KEY="your_key"
heroku config:set OPENAI_BASE_URL="https://aipipe.org/openai/v1"
git push heroku main
```

### 📊 Performance Optimization

#### For Production:
1. **Gunicorn Configuration** (optional):
```bash
# Install gunicorn
pip install gunicorn

# Update start command
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:$PORT
```

2. **Environment Variables**:
- Set `PYTHONUNBUFFERED=1` for better logging
- Set `PORT` if required by platform

### 🔍 Troubleshooting

#### Common Issues:
1. **Port Binding**: Ensure `run.py` uses `PORT` environment variable
2. **Dependencies**: Verify all packages in `requirements.txt`
3. **Memory**: Render free tier has 512MB limit
4. **Timeout**: API responses must complete within 30 seconds

#### Logs:
- Check Render dashboard for deployment logs
- Monitor application logs for errors
- Use `print()` statements for debugging

### 🎯 Testing Deployed API

#### Health Check:
```bash
curl https://your-app.onrender.com/
```

#### Titanic Analysis Test:
```bash
curl -X POST "https://your-app.onrender.com/api/" \
  -F "files=@test_questions.txt" \
  -F "files=@sample_data.csv"
```

Expected Response:
```json
[1, "Titanic", 0.485782, "data:image/png;base64,..."]
```

### 📝 Notes
- First deployment may take 5-10 minutes
- Free tier may have cold start delays
- Monitor usage to avoid limits
- Keep API key secure in environment variables

### 🆘 Support
If deployment fails:
1. Check build logs in Render dashboard
2. Verify all files are committed to Git
3. Ensure environment variables are set correctly
4. Test locally first with `python run.py`
