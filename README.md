# Face Swap AI - Netlify Deployment

## 🚀 Quick Deploy to Netlify

### 1. Connect Repository
- Push this code to your GitHub repository
- Connect your GitHub repo to Netlify

### 2. Environment Variables
Set these in Netlify dashboard > Site settings > Environment variables:
- `GEMINI_API_KEY` - Your Google Gemini API key
- `SECRET_KEY` - Random string for session security

### 3. Build Settings
Netlify will automatically detect the build settings from `netlify.toml`:
- Build command: `echo 'Build complete'`
- Publish directory: `static`
- Functions directory: `netlify/functions`

### 4. Deploy
- Click "Deploy site" in Netlify
- Your site will be live at `https://your-site-name.netlify.app`

## 📁 File Structure
```
├── netlify.toml              # Netlify configuration
├── package.json              # Node.js package info
├── static/                   # Static files and templates
├── netlify/functions/        # Serverless functions
│   ├── generate.py          # Face swap API
│   ├── admin-upload.py      # Template upload API
│   └── admin-delete.py      # Template delete API
├── templates/               # HTML templates (for reference)
└── app.py                   # Original Flask app (for reference)
```

## 🔧 Admin Access
- URL: `your-site.netlify.app/admin`
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
For deployment issues, check Netlify documentation or contact support.
