"""
ScrapeOps client implementation for making HTTP requests through the ScrapeOps proxy service.
This module provides a replacement for the requests.Session class used in the YouTube transcript API.
"""
import requests
import json
from urllib.parse import urlencode
from typing import Dict, Optional, Union
import logging

# Set up logging
logger = logging.getLogger(__name__)

class ScrapeOpsClient:
    """
    Client for making HTTP requests through ScrapeOps proxy service.
    This class mimics the interface of requests.Session that's needed by the YouTube transcript API.
    """
    
    def __init__(self, api_key: str, timeout: int = 120):
        """
        Initialize the ScrapeOps client.
        
        Args:
            api_key: Your ScrapeOps API key
            timeout: Request timeout in seconds (default: 120)
        """
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {}
        self.cookies = requests.cookies.RequestsCookieJar()
        self.proxies = {}
    
    def get(self, url: str, params: Optional[Dict] = None) -> requests.Response:
        """
        Make a GET request through the ScrapeOps proxy.
        
        Args:
            url: The URL to request
            params: Optional query parameters
            
        Returns:
            A requests.Response object
        """
        logger.debug(f"Making GET request to {url} through ScrapeOps")
        
        # Determine if this is a YouTube request
        is_youtube = 'youtube.com' in url or 'youtu.be' in url
        
        # Prepare ScrapeOps proxy parameters
        proxy_params = {
            'api_key': self.api_key,
            'url': url,
            'optimize_request': 'true',  # Optimize the request for target websites
            'render_js': 'false',        # We don't need JavaScript rendering for YouTube transcripts
            'keep_headers': 'true',      # Keep original headers in the response
            'country': 'us',             # Use US IP addresses for YouTube
        }
        
        # Add parameters if provided
        if params:
            # Build a query string from the params dictionary
            if '?' in url:
                # URL already has parameters
                param_str = '&'.join(f"{k}={v}" for k, v in params.items())
                proxy_params['url'] = f"{url}&{param_str}"
            else:
                # URL doesn't have parameters yet
                param_str = '&'.join(f"{k}={v}" for k, v in params.items())
                proxy_params['url'] = f"{url}?{param_str}"
        
        # Add YouTube-specific optimizations
        if is_youtube:
            # Set premium flag for YouTube
            proxy_params['premium'] = 'true'
            # Use a standard YouTube browser profile
            proxy_params['browser_type'] = 'chrome'
        
        # Add custom headers if specified
        if self.headers:
            # Add default YouTube-friendly headers if not already specified
            if is_youtube and 'User-Agent' not in self.headers:
                self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            if is_youtube and 'Accept-Language' not in self.headers:
                self.headers['Accept-Language'] = 'en-US,en;q=0.9'
                
            proxy_params['headers'] = json.dumps(dict(self.headers))
            
        # Add cookies if present
        if len(self.cookies) > 0:
            # Convert cookies to a format ScrapeOps can use
            cookie_dict = requests.utils.dict_from_cookiejar(self.cookies)
            proxy_params['cookies'] = json.dumps(cookie_dict)
        
        try:
            # Make the request through ScrapeOps proxy
            scrapeops_response = requests.get(
                url='https://proxy.scrapeops.io/v1/',
                params=proxy_params,
                timeout=self.timeout,
            )
            
            # Log the actual URL being requested for debugging
            logger.debug(f"ScrapeOps API called with response status: {scrapeops_response.status_code}")
            
            # Create a new response object that mimics what YouTube API expects
            response = requests.Response()
            
            # Check if we got a successful response from ScrapeOps
            if scrapeops_response.status_code == 200:
                try:
                    # Try to parse as JSON first
                    scrapeops_data = scrapeops_response.json()
                    
                    if 'html' in scrapeops_data:
                        # Set the content to the HTML from ScrapeOps
                        response._content = scrapeops_data['html'].encode('utf-8')
                        response.status_code = 200
                    else:
                        # If 'html' is not in the response, use the raw content
                        logger.warning("No 'html' field in ScrapeOps JSON response, using raw content")
                        response._content = scrapeops_response.content
                        response.status_code = 200
                        
                except json.JSONDecodeError:
                    # If not valid JSON, assume it's raw HTML content
                    logger.debug("ScrapeOps response is not JSON, using as raw HTML")
                    response._content = scrapeops_response.content
                    response.status_code = 200
                    
            else:
                # If ScrapeOps request failed, pass through the error
                logger.error(f"ScrapeOps API returned error status: {scrapeops_response.status_code}")
                response.status_code = scrapeops_response.status_code
                response._content = scrapeops_response.content
                
            # Set other properties of the response
            response.url = url
            response.request = requests.Request(method='GET', url=url).prepare()
            response.encoding = 'utf-8'
            
            return response
            
        except Exception as e:
            # Log any exceptions during the request
            logger.error(f"Error making ScrapeOps request: {str(e)}")
            
            # Create an error response
            error_response = requests.Response()
            error_response.status_code = 500
            error_response._content = str(e).encode('utf-8')
            error_response.url = url
            error_response.request = requests.Request(method='GET', url=url).prepare()
            
            return error_response 