import json
import os
import uuid
import mimetypes
import base64
from google import genai
from google.genai import types

# Constants
FACE_SWAP_PROMPT = """Make the person's face from picture number 1 replace the face in picture number 2.
You can change the clothes but only one thing: don't change the hairstyle or anything about the character from picture number 1.
Keep the same face of the person from picture one, don't change anything about their skin or face.
Change the position of the person to make the picture look natural and well composed.

Picture 1 is the user's face photo.
Picture 2 is the template/background image.

Create the final image with the face from picture 1 placed onto picture 2's scene/pose."""

IMAGE_SIZES = {"x1": "1K", "1k": "1K", "2k": "2K", "4k": "4K"}

def generate_face_swap(user_image_path, template_image_path, image_size="2K", aspect_ratio=None):
    """Generate face swap using Gemini API"""
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        # Load both images
        user_image_data = load_image_as_base64(user_image_path)
        template_image_data = load_image_as_base64(template_image_path)

        user_mime = get_mime_type(user_image_path)
        template_mime = get_mime_type(template_image_path)

        model = "gemini-3-pro-image-preview"

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
            image_config=types.ImageConfig(image_size=image_size),
        )

        generated_files = []
        text_response = ""

        for chunk in client.models.generate_content_stream(
            model=model, contents=contents, config=generate_content_config,
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
                data_buffer = part.inline_data.data
                file_extension = mimetypes.guess_extension(part.inline_data.mime_type) or '.png'
                file_name = f"{file_id}{file_extension}"
                generated_files.append({
                    'filename': file_name,
                    'data': base64.b64encode(data_buffer).decode('utf-8'),
                    'mime_type': part.inline_data.mime_type
                })
            elif hasattr(part, 'text') and part.text:
                text_response += part.text

        return generated_files, text_response
    except Exception as e:
        return [], str(e)

def load_image_as_base64(file_path):
    """Load image file and return base64 encoded data"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def get_mime_type(file_path):
    """Get MIME type from file path"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'image/png'

def handler(event, context):
    """Netlify Function handler for face swap"""
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

    try:
        # Parse form data
        body = event.get('body', '')
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body).decode('utf-8')

        # For simplicity, assume JSON body with base64 encoded images
        data = json.loads(body)
        user_photo_data = data.get('user_photo')
        template_id = data.get('template_id')
        image_size = data.get('image_size', 'x1')
        aspect_ratio = data.get('aspect_ratio', '')

        if not user_photo_data or not template_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }

        # Save user photo temporarily
        user_filename = f"user_{uuid.uuid4()}.png"
        user_path = f"/tmp/{user_filename}"
        with open(user_path, "wb") as f:
            f.write(base64.b64decode(user_photo_data))

        # Template path (assuming templates are stored in static/templates_gallery)
        template_path = f"static/templates_gallery/{template_id}"
        if not os.path.exists(template_path):
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Template not found'})
            }

        # Generate face swap
        size = IMAGE_SIZES.get(image_size, "2K")
        files, text = generate_face_swap(
            user_path, template_path, image_size=size,
            aspect_ratio=aspect_ratio if aspect_ratio else None
        )

        # Clean up temp file
        if os.path.exists(user_path):
            os.remove(user_path)

        if files:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'images': [{
                        'filename': img['filename'],
                        'data': img['data'],
                        'mime_type': img['mime_type']
                    } for img in files],
                    'text': text
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Generation failed'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
