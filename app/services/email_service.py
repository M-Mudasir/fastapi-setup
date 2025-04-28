import logging
import requests
import httpx
from app.core.config import settings


async def send_email(email_address, html_template, subject):
    """
    Send an email using the Azure Logic App endpoint asynchronously.
    
    Args:
        email_address (str): Recipient's email address
        html_template (str): HTML content of the email
        subject (str): Subject line of the email
        
    Returns:
        aiohttp.ClientResponse: The response from the API
    """
    url = settings.EMAIL_LOGIC_APP_URL
    
    # Query parameters
    params = {
        "api-version": "2016-06-01",
        "sp": "/triggers/manual/run",
        "sv": "1.0",
        "sig": settings.EMAIL_LOGIC_APP_KEY
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "Email": email_address,
        "HtmlTemplate": html_template,
        "Subject": subject
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params, headers=headers, json=data)

        if response.status_code < 300:
            print(f"Email sent successfully to {email_address}")
        else:
            print(f"Failed to send email. Status code: {response.status_code}")
            print(f"Response: {response.text}")
        
        return response