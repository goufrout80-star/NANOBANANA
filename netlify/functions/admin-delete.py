import json
import os

def handler(event, context):
    """Netlify Function handler for admin template deletion"""
    if event['httpMethod'] != 'DELETE':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

    # Check for admin authentication
    auth_header = event.get('headers', {}).get('authorization', '')
    if auth_header != 'Bearer admin-2':
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Unauthorized'})
        }

    try:
        # Get filename from path parameters or query
        filename = event.get('path', '').split('/')[-1]  # Extract from /admin/delete/filename

        if not filename:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No filename provided'})
            }

        filepath = f"static/templates_gallery/{filename}"

        if os.path.exists(filepath):
            os.remove(filepath)
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': True})
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'File not found'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
