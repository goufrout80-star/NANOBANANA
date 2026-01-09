# Face Swap AI - Hostinger Deployment

## 🚀 Quick Deploy to Hostinger

### 1. Upload Files
- Upload all files in this folder to your Hostinger public_html directory
- Make sure to preserve the folder structure

### 2. Environment Setup
- Set up Python environment in Hostinger cPanel
- Install required packages from `requirements.txt`

### 3. Environment Variables
- Create a `.env` file with your `GEMINI_API_KEY`
- Set `SECRET_KEY` for session management

### 4. Configure App
- Point your domain to the uploaded files
- Set up Python application in Hostinger to run `wsgi.py`

## 📁 File Structure
```
├── app.py              # Main Flask application
├── wsgi.py             # WSGI entry point for Hostinger
├── .htaccess           # Apache configuration
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── static/            # Static files (CSS, images, uploads)
└── templates/         # HTML templates
```

## 🔧 Admin Access
- URL: `yourdomain.com/admin`
- Username: `admin`
- Password: `2`

## 🎨 Features
- Face swap AI using Gemini 3 Pro
- Template management system
- User photo upload
- Multiple image sizes (1K, 2K, 4K)
- Aspect ratio options
- Modern UI with custom color scheme

## 📞 Support
For deployment issues, check Hostinger Python hosting documentation.
