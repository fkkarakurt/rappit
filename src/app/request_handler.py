# src/app/request_handler.py - ORJİNAL
import requests
import json
import time
from urllib.parse import urlparse
from typing import Optional, Dict, Any

class RequestHandler:
    """
    Handles the core logic for sending HTTP requests and processing the
    received responses. It uses the 'requests' library and maintains a session
    to manage cookies and connection pooling across multiple requests.
    """
    def __init__(self):
        """
        Initializes the handler with a persistent requests session.
        """
        self.session = requests.Session()
        self.last_response: Optional[requests.Response] = None
        # Default to secure - session oluşturulduktan SONRA set et
        self.session.verify = True

    def send_request(self, method: str, url: str, headers: Optional[Dict[str, str]] = None,
                     body: Optional[str] = None, content_type: str = "application/json") -> Dict[str, Any]:
        """
        Sends an HTTP request with the specified method, URL, headers, and body.

        Args:
            method (str): The HTTP method (GET, POST, PUT, etc.).
            url (str): The target URL.
            headers (dict, optional): Custom headers to send. Defaults to None.
            body (str, optional): The raw request body content. Defaults to None.
            content_type (str): The Content-Type header to use if a body is present and Content-Type is missing.

        Returns:
            dict: A formatted dictionary containing essential response details or error information.
        """
        try:
            # --- 1. Prepare Headers and Body ---

            # Create a mutable copy of the input headers
            request_headers = headers.copy() if headers else {}

            # Auto-set Content-Type for methods that typically include a body, if not already set
            if body and method in ['POST', 'PUT', 'PATCH']:
                if 'Content-Type' not in request_headers:
                    request_headers['Content-Type'] = content_type

            # Determine how to send the body (as JSON dict or raw data)
            data = None
            if body and body.strip():
                if content_type == 'application/json':
                    try:
                        # Attempt to parse the body as JSON; if successful, use the 'json' argument in requests
                        data = json.loads(body)
                    except json.JSONDecodeError:
                        # If parsing fails, treat the body as raw string data
                        data = body
                else:
                    # Treat non-JSON content types as raw string data
                    data = body

            # --- 2. Send Request and Measure Time ---
            start_time = time.time()

            # Execute the request using the session
            response = self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                # 'requests' library handles serializing dicts passed to 'json', or sends raw data passed to 'data'
                json=data if isinstance(data, dict) else None,
                data=data if not isinstance(data, dict) else None,
                timeout=30, # Set a timeout to prevent indefinite waiting
                verify=self.session.verify  # Use session setting
            )

            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)

            # --- 3. Format Response ---
            formatted_response = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': response.text,
                'response_time': response_time, # Time in milliseconds
                'size': len(response.content), # Size in bytes
                'url': response.url, # Final URL after redirects
                'method': method,
                'reason': response.reason # Status reason phrase (e.g., 'OK', 'Not Found')
            }

            self.last_response = response
            return formatted_response

        except requests.exceptions.RequestException as e:
            # Handle all exceptions related to the request (e.g., connection errors, timeouts)
            return {
                'error': str(e),
                'status_code': 0, # Use 0 to indicate a network/client error, not an HTTP status
                'response_time': 0,
                'body': f'Request Error: {str(e)}'
            }

    def validate_url(self, url: str) -> bool:
        """
        Performs a basic validation to check if the string represents a syntactically
        valid URL (must have a scheme like 'http' and a network location).

        Args:
            url (str): The URL string to validate.

        Returns:
            bool: True if the URL is valid, False otherwise.
        """
        try:
            result = urlparse(url)
            # A valid URL must have a scheme (e.g., http, https) and a network location (e.g., example.com)
            return all([result.scheme, result.netloc])
        except:
            return False

    def set_ssl_verification(self, verify: bool):
        """
        Set SSL certificate verification

        Args:
            verify (bool): Whether to verify SSL certificates
        """
        self.session.verify = verify
