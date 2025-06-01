import boto3
import json
import os
from urllib.parse import unquote_plus

def lambda_handler(event, context):
    """
    Netflix-style video streaming from S3
    Bucket: my-aws-bucket-543
    Default Video: Baraa Masoud - Rahmatun Lil'Alamen (COVER)
    API Gateway: https://8uczgph2te.execute-api.us-east-1.amazonaws.com/default/serverless-architecture
    """
    
    # Configuration
    config = {
        'S3_BUCKET': 'my-aws-bucket-543',
        'DEFAULT_VIDEO': 'Baraa Masoud - Rahmatun Lil\'Alamen (COVER) - - Vocals Only براء مسعود - رحمة للعالمين - بدون موسيقى.mp4',
        'PRESIGNED_URL_EXPIRY': 3600,  # 1 hour expiration
        'SITE_TITLE': 'ServerlessFlix',
        'FAVICON': 'https://cdn-icons-png.flaticon.com/512/5977/5977590.png'
    }
    
    try:
        # Get requested video filename
        video_filename = config['DEFAULT_VIDEO']
        if 'queryStringParameters' in event and event['queryStringParameters']:
            if 'video' in event['queryStringParameters']:
                video_filename = unquote_plus(event['queryStringParameters']['video'])
        
        # Create S3 client and verify file exists
        s3_client = boto3.client('s3')
        try:
            s3_client.head_object(Bucket=config['S3_BUCKET'], Key=video_filename)
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return error_response(404, f'Video "{video_filename}" not found')
            raise
        
        # Generate presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': config['S3_BUCKET'], 'Key': video_filename},
            ExpiresIn=config['PRESIGNED_URL_EXPIRY']
        )
        
        # Netflix-style HTML response
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{config['SITE_TITLE']} - {video_filename}</title>
            <link rel="icon" href="{config['FAVICON']}" type="image/png">
            <style>
                :root {{
                    --primary: #e50914;
                    --dark: #141414;
                    --light: #f3f3f3;
                }}
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    background-color: var(--dark);
                    color: var(--light);
                }}
                
                .navbar {{
                    padding: 1rem 4%;
                    height: 68px;
                    display: flex;
                    align-items: center;
                    background: linear-gradient(to bottom, rgba(0,0,0,0.7) 10%, transparent);
                    position: fixed;
                    width: 100%;
                    top: 0;
                    z-index: 100;
                }}
                
                .logo {{
                    color: var(--primary);
                    font-size: 1.8rem;
                    font-weight: bold;
                    text-decoration: none;
                }}
                
                .player-container {{
                    padding-top: 56.25%; /* 16:9 Aspect Ratio */
                    position: relative;
                    margin-top: 68px;
                }}
                
                .video-player {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: #000;
                }}
                
                .video-info {{
                    padding: 2rem 4%;
                    max-width: 800px;
                    margin: 0 auto;
                }}
                
                .video-title {{
                    font-size: 1.5rem;
                    margin-bottom: 1rem;
                }}
                
                .download-btn {{
                    display: inline-block;
                    background: var(--primary);
                    color: white;
                    padding: 0.5rem 1.5rem;
                    border-radius: 4px;
                    text-decoration: none;
                    margin-top: 1rem;
                    transition: all 0.3s;
                }}
                
                .download-btn:hover {{
                    background: #f40612;
                }}
                
                @media (max-width: 768px) {{
                    .navbar {{
                        padding: 1rem;
                    }}
                    .video-info {{
                        padding: 1.5rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <nav class="navbar">
                <a href="#" class="logo">{config['SITE_TITLE']}</a>
            </nav>
            
            <div class="player-container">
                <video class="video-player" controls autoplay>
                    <source src="{presigned_url}" type="video/mp4">
                    Your browser does not support HTML5 video.
                </video>
            </div>
            
            <div class="video-info">
                <h1 class="video-title">{video_filename}</h1>
                <a href="{presigned_url}" class="download-btn" download>Download Video</a>
                <p style="margin-top: 1rem; color: #777;">Link expires in 1 hour</p>
            </div>
            
            <script>
                // Auto-fullscreen on mobile devices
                if (window.innerWidth <= 768) {{
                    document.querySelector('.video-player').requestFullscreen();
                }}
                
                // Keep track of playback position
                const video = document.querySelector('.video-player');
                video.addEventListener('timeupdate', () => {{
                    localStorage.setItem('{video_filename}_time', video.currentTime);
                }});
                
                // Resume playback if available
                const savedTime = localStorage.getItem('{video_filename}_time');
                if (savedTime) {{
                    video.addEventListener('canplay', () => {{
                        video.currentTime = parseFloat(savedTime);
                    }});
                }}
            </script>
        </body>
        </html>
        """
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*'
            },
            'body': html
        }
        
    except Exception as e:
        return error_response(500, str(e))

def error_response(status_code, message):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': message})
    }