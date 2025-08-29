import boto3
from botocore.exceptions import ClientError
from loguru import logger

def send_email(recipient_email, subject, body, sender_email='patrik@aidriatic.com'):
    """
    Send an email using AWS SES
    
    Args:
        recipient_email (str): Email address of the recipient
        subject (str): Subject line of the email
        body (str): Body content of the email
        sender_email (str): Sender email address (default: patrik@aidriatic.com)
    
    Returns:
        dict: Response from AWS SES or error information
    """
    ses_client = boto3.client('ses',)
    
    try:
        response = ses_client.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': [recipient_email]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        return {
            'success': True,
            'message_id': response['MessageId'],
            'message': f"Email sent successfully to {recipient_email}"
        }
    except ClientError as e:
        return {
            'success': False,
            'error': e.response['Error']['Message'],
            'message': f"Failed to send email to {recipient_email}"
        }

def send_html_email(recipient_email, subject, html_body, text_body=None, sender_email='patrik@aidriatic.com'):
    """
    Send an HTML email using AWS SES
    
    Args:
        recipient_email (str): Email address of the recipient
        subject (str): Subject line of the email
        html_body (str): HTML content of the email
        text_body (str): Plain text fallback (optional)
        sender_email (str): Sender email address (default: patrik@aidriatic.com)
    
    Returns:
        dict: Response from AWS SES or error information
    """
    ses_client = boto3.client('ses', region_name='eu-central-1')
    
    # Create the email body structure
    body_content = {
        'Html': {
            'Data': html_body,
            'Charset': 'UTF-8'
        }
    }
    
    # Add text version if provided
    if text_body:
        body_content['Text'] = {
            'Data': text_body,
            'Charset': 'UTF-8'
        }
    
    try:
        response = ses_client.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': [recipient_email]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': body_content
            }
        )
        return {
            'success': True,
            'message_id': response['MessageId'],
            'message': f"HTML email sent successfully to {recipient_email}"
        }
    except ClientError as e:
        return {
            'success': False,
            'error': e.response['Error']['Message'],
            'message': f"Failed to send HTML email to {recipient_email}"
        }

# Example usage
if __name__ == "__main__":
    # Test sending a plain text email
    result = send_email(
        recipient_email="test@example.com",
        subject="Hello from aidriatic.com",
        body="This is a test email sent from my custom domain using AWS SES!"
    )
    
    if result['success']:
        print(f"✓ {result['message']}")
        print(f"Message ID: {result['message_id']}")
    else:
        print(f"✗ {result['message']}")
        print(f"Error: {result['error']}")
    
    # Test sending an HTML email
    html_content = """
    <html>
        <body>
            <h1>Hello from aidriatic.com</h1>
            <p>This is an <strong>HTML email</strong> sent from my custom domain!</p>
            <p>Visit my website: <a href="https://aidriatic.com">aidriatic.com</a></p>
        </body>
    </html>
    """
    
    html_result = send_html_email(
        recipient_email="test@example.com",
        subject="HTML Test from aidriatic.com",
        html_body=html_content,
        text_body="This is the plain text version of the email."
    )
    
    if html_result['success']:
        print(f"✓ {html_result['message']}")
        print(f"Message ID: {html_result['message_id']}")
    else:
        print(f"✗ {html_result['message']}")
        print(f"Error: {html_result['error']}")