import os
import uuid
import mimetypes
import base64
import json
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session
from google import genai
from google.genai import types
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "faceswap-secret-key-2024")

# Folders
BASE_DIR = os.path.dirname(__file__)
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'generated')
app.config['TEMPLATES_FOLDER'] = os.path.join(BASE_DIR, 'static', 'templates_gallery')
app.config['USER_UPLOADS'] = os.path.join(BASE_DIR, 'static', 'user_uploads')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMPLATES_FOLDER'], exist_ok=True)
os.makedirs(app.config['USER_UPLOADS'], exist_ok=True)

# Admin credentials
ADMIN_USER = "admin"
ADMIN_PASS = "2"

# Image size mappings
IMAGE_SIZES = {
    "x1": "1K",
    "1k": "1K",
    "2k": "2K",
    "4k": "4K"
}

# Aspect ratios
ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"]

# Face swap prompt template
FACE_SWAP_PROMPT = """Make the person's face from picture number 1 replace the face in picture number 2. 
You can change the clothes but only one thing: don't change the hairstyle or anything about the character from picture number 1.
Keep the same face of the person from picture one, don't change anything about their skin or face.
Change the position of the person to make the picture look natural and well composed.

Picture 1 is the user's face photo.
Picture 2 is the template/background image.

Create the final image with the face from picture 1 placed onto picture 2's scene/pose."""


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def load_image_as_base64(file_path):
    """Load image file and return base64 encoded data"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')


def get_mime_type(file_path):
    """Get MIME type from file path"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'image/png'


def generate_face_swap(user_image_path, template_image_path, image_size="2K", aspect_ratio=None):
    """Generate face swap using Gemini API"""
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    # Load both images
    user_image_data = load_image_as_base64(user_image_path)
    template_image_data = load_image_as_base64(template_image_path)
    
    user_mime = get_mime_type(user_image_path)
    template_mime = get_mime_type(template_image_path)

    model = "gemini-3-pro-image-preview"
    
    # Build prompt with aspect ratio if specified
    prompt = FACE_SWAP_PROMPT
    if aspect_ratio:
        prompt += f"\n\nGenerate the output image with aspect ratio {aspect_ratio}."

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="Picture 1 (User's face):"),
                types.Part.from_bytes(data=base64.b64decode(user_image_data), mime_type=user_mime),
                types.Part.from_text(text="Picture 2 (Template/Background):"),
                types.Part.from_bytes(data=base64.b64decode(template_image_data), mime_type=template_mime),
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
        image_config=types.ImageConfig(
            image_size=image_size,
        ),
    )

    generated_files = []
    text_response = ""

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        
        part = chunk.candidates[0].content.parts[0]
        if part.inline_data and part.inline_data.data:
            file_id = str(uuid.uuid4())
            inline_data = part.inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type) or '.png'
            file_name = f"{file_id}{file_extension}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
            
            with open(file_path, "wb") as f:
                f.write(data_buffer)
            
            generated_files.append(file_name)
        elif hasattr(part, 'text') and part.text:
            text_response += part.text

    return generated_files, text_response


def get_templates():
    """Get all template images from gallery"""
    templates = []
    folder = app.config['TEMPLATES_FOLDER']
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                templates.append({
                    'filename': filename,
                    'path': f'/static/templates_gallery/{filename}'
                })
    return templates


# ============ USER ROUTES ============

@app.route('/')
def index():
    templates = get_templates()
    return render_template('index.html', templates=templates, aspect_ratios=ASPECT_RATIOS)


@app.route('/swap', methods=['POST'])
def swap():
    if 'user_photo' not in request.files:
        return jsonify({'error': 'Please upload your photo'}), 400
    
    user_photo = request.files['user_photo']
    template_id = request.form.get('template_id')
    image_size = request.form.get('image_size', 'x1')
    aspect_ratio = request.form.get('aspect_ratio', '')
    
    if not user_photo.filename:
        return jsonify({'error': 'Please select a photo'}), 400
    
    if not template_id:
        return jsonify({'error': 'Please select a template'}), 400
    
    if not os.environ.get("GEMINI_API_KEY"):
        return jsonify({'error': 'GEMINI_API_KEY not configured'}), 500
    
    # Save user photo
    user_filename = f"{uuid.uuid4()}_{user_photo.filename}"
    user_path = os.path.join(app.config['USER_UPLOADS'], user_filename)
    user_photo.save(user_path)
    
    # Get template path
    template_path = os.path.join(app.config['TEMPLATES_FOLDER'], template_id)
    if not os.path.exists(template_path):
        return jsonify({'error': 'Template not found'}), 404
    
    # Map image size
    size = IMAGE_SIZES.get(image_size, "2K")
    
    try:
        files, text = generate_face_swap(
            user_path, 
            template_path, 
            image_size=size,
            aspect_ratio=aspect_ratio if aspect_ratio else None
        )
        return jsonify({
            'success': True,
            'images': [f'/static/generated/{f}' for f in files],
            'text': text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ ADMIN ROUTES ============

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    templates = get_templates()
    return render_template('admin.html', templates=templates)


@app.route('/admin/upload', methods=['POST'])
@admin_required
def admin_upload():
    if 'template' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['template']
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400
    
    # Save template
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(app.config['TEMPLATES_FOLDER'], filename)
    file.save(filepath)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'path': f'/static/templates_gallery/{filename}'
    })


@app.route('/admin/delete/<filename>', methods=['DELETE'])
@admin_required
def admin_delete(filename):
    filepath = os.path.join(app.config['TEMPLATES_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'success': True})
    return jsonify({'error': 'File not found'}), 404


# ============ STATIC FILES ============

@app.route('/static/generated/<filename>')
def serve_generated(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/static/templates_gallery/<filename>')
def serve_template(filename):
    return send_from_directory(app.config['TEMPLATES_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
