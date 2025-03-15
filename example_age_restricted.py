#!/usr/bin/env python3
"""
Example script demonstrating how to use ScrapeOps to access age-restricted YouTube videos.
This script combines ScrapeOps with cookie-based authentication for maximum reliability.

Usage:
    python example_age_restricted.py <video_id> <scrapeops_api_key> [cookie_path]
"""
import sys
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from youtube_transcript_api import YouTubeTranscriptApi, ScrapeOpsClient
from youtube_transcript_api._errors import AgeRestricted

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_transcript_with_scrapeops(video_id: str, api_key: str, cookie_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Attempt to get a transcript using ScrapeOps, with optional cookie authentication.
    
    Args:
        video_id: YouTube video ID
        api_key: ScrapeOps API key
        cookie_path: Optional path to YouTube cookie file (Mozilla/Netscape format)
        
    Returns:
        Dictionary with transcript data and metadata
    """
    # Initialize ScrapeOps client with custom configuration
    scrapeops_client = ScrapeOpsClient(
        api_key=api_key,
        timeout=180  # Increase timeout to 3 minutes
    )
    
    # # Use more browser-like headers to improve chances of success
    # scrapeops_client.headers.update({
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    #     "Accept-Language": "en-US,en;q=0.9",
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    #     "Referer": "https://www.youtube.com/",
    #     "DNT": "1",
    #     "Upgrade-Insecure-Requests": "1"
    # })
    
    # Create API instance with ScrapeOps client and optional cookie path
    ytt_api = YouTubeTranscriptApi(
        http_client=scrapeops_client,
        cookie_path=Path(cookie_path) if cookie_path else None
    )
    
    # First, try to list available transcripts
    try:
        transcript_list = ytt_api.list(video_id)
        logger.info(f"Successfully accessed video {video_id}")
        logger.info("Available transcripts:")
        for transcript in transcript_list:
            logger.info(f"  - {transcript.language} ({transcript.language_code}), Generated: {transcript.is_generated}")
    except AgeRestricted:
        if not cookie_path:
            logger.error("Video is age-restricted and no cookies provided. Authentication is required.")
            raise
        else:
            logger.warning("Video is age-restricted, but cookies were provided. Continuing with authentication...")
    except Exception as e:
        logger.error(f"Error listing transcripts: {type(e).__name__}: {e}")
        raise
        
    # Try to fetch the transcript in English first, then any available language
    try:
        transcript = ytt_api.fetch(video_id, languages=['en', '*'])
        
        # Create result with metadata
        result = {
            'video_id': video_id,
            'language': transcript.language,
            'language_code': transcript.language_code,
            'is_generated': transcript.is_generated,
            'snippet_count': len(transcript),
            'transcript': transcript.to_raw_data()
        }
        
        logger.info(f"Successfully retrieved transcript with {len(transcript)} snippets")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching transcript: {type(e).__name__}: {e}")
        raise


def main() -> None:
    """Main function to run the age-restricted video example."""
    # Check command line arguments
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <video_id> <scrapeops_api_key> [cookie_path]")
        sys.exit(1)
        
    video_id = sys.argv[1]
    api_key = sys.argv[2]
    cookie_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    logger.info(f"Attempting to fetch transcript for video {video_id}")
    if cookie_path:
        logger.info(f"Using cookie file: {cookie_path}")
    else:
        logger.info("No cookie file provided")
    
    try:
        result = get_transcript_with_scrapeops(video_id, api_key, cookie_path)
        
        # Print brief summary
        print("\nTranscript Summary:")
        print(f"Video ID: {result['video_id']}")
        print(f"Language: {result['language']} ({result['language_code']})")
        print(f"Auto-generated: {result['is_generated']}")
        print(f"Number of snippets: {result['snippet_count']}")
        
        # Print sample of transcript
        print("\nSample of transcript:")
        for snippet in result['transcript'][:5]:  # First 5 snippets
            start_time = snippet['start']
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            print(f"[{minutes:02d}:{seconds:02d}] {snippet['text']}")
        
        print(f"\n... and {result['snippet_count'] - 5} more snippets")
        
    except AgeRestricted:
        print("\nThis video is age-restricted and requires authentication.")
        print("Please provide a YouTube cookie file to access this content.")
        print("You can use browser extensions like 'Cookie-Editor' (Chrome) or 'cookies.txt' (Firefox)")
        print("to export your YouTube cookies in Netscape format.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\nError: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 