import json
import os
import uuid
import base64

def handler(event, context):
    """Netlify Function handler for admin template upload"""
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

    # Check for admin authentication (simplified for demo)
    auth_header = event.get('headers', {}).get('authorization', '')
    if auth_header != 'Bearer admin-2':  # Simple auth for demo
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Unauthorized'})
        }

    try:
        # Parse form data
        body = event.get('body', '')
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body).decode('utf-8')

        data = json.loads(body)
        template_data = data.get('template')

        if not template_data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No template data provided'})
            }

        # Save template
        filename = f"{uuid.uuid4()}.png"
        filepath = f"static/templates_gallery/{filename}"

        # Ensure directory exists
        os.makedirs("static/templates_gallery", exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(base64.b64decode(template_data))

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'filename': filename,
                'path': f'/static/templates_gallery/{filename}'
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
