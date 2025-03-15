#!/usr/bin/env python3
"""
Example script demonstrating how to use the YouTube Transcript API with ScrapeOps integration.
This script shows both basic and advanced usage patterns.

Usage:
    python example_scrapeops.py <scrapeops_api_key> [video_id1 video_id2 ...]
"""
import sys
import logging
import json
import traceback
from typing import List, Dict, Any

from youtube_transcript_api import YouTubeTranscriptApi, ScrapeOpsClient
from youtube_transcript_api.formatters import JSONFormatter, WebVTTFormatter

# Configure logging - use DEBUG level for more detailed logs
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Some YouTube videos known to have transcripts
SAMPLE_VIDEOS = [
    "9bZkp7q19f0",  # Gangnam Style
    "dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
    "jNQXAC9IVRw",  # Me at the zoo (first YouTube video)
    "Mh4f9AYRCZY",  # TED Talk
    "8jPQjjsBbIc",  # Tutorial video
]

def basic_usage(video_id: str, api_key: str) -> bool:
    """
    Demonstrates basic usage of the ScrapeOps integration.
    
    Args:
        video_id: YouTube video ID
        api_key: ScrapeOps API key
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Demonstrating basic usage with ScrapeOps integration for video {video_id}")
    
    # Initialize the API with ScrapeOps API key
    ytt_api = YouTubeTranscriptApi(scrapeops_api_key=api_key)
    
    # Fetch transcript
    try:
        transcript = ytt_api.fetch(video_id)
        
        # Print transcript details
        logger.info(f"Retrieved transcript for video {video_id}")
        logger.info(f"Language: {transcript.language} ({transcript.language_code})")
        logger.info(f"Is generated: {transcript.is_generated}")
        logger.info(f"Number of snippets: {len(transcript)}")
        
        # Print the first 3 snippets
        logger.info("First 3 snippets:")
        for i, snippet in enumerate(transcript[:3]):
            logger.info(f"  {i+1}. [{snippet.start:.2f}s]: {snippet.text}")
            
        # Success!
        return True
            
    except Exception as e:
        logger.error(f"Error fetching transcript for video {video_id}: {str(e)}")
        logger.debug("Detailed traceback:", exc_info=True)
        return False


def advanced_usage(video_id: str, api_key: str) -> bool:
    """
    Demonstrates advanced usage of the ScrapeOps integration with custom client configuration.
    
    Args:
        video_id: YouTube video ID
        api_key: ScrapeOps API key
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Demonstrating advanced usage with custom ScrapeOpsClient for video {video_id}")
    
    # Create a custom ScrapeOps client with custom configuration
    scrapeops_client = ScrapeOpsClient(
        api_key=api_key,
        timeout=180  # Increase timeout to 3 minutes
    )
    
    # Configure custom headers to appear more like a regular browser
    # scrapeops_client.headers.update({
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    #     "Accept-Language": "en-US,en;q=0.9",
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    #     "Referer": "https://www.youtube.com/",
    # })
    
    # Initialize the API with the custom client
    ytt_api = YouTubeTranscriptApi(http_client=scrapeops_client)
    
    try:
        # First try to simply list available transcripts
        transcript_list = ytt_api.list(video_id)
        
        logger.info(f"Available transcripts for video {video_id}:")
        for transcript in transcript_list:
            logger.info(f"  - {transcript.language} ({transcript.language_code}), Generated: {transcript.is_generated}, Translatable: {transcript.is_translatable}")
        
        # Try to find a transcript in English or any available language
        transcript = transcript_list.find_transcript(['en', '*'])
        
        # Fetch the transcript
        fetched_transcript = transcript.fetch()
        
        # Print transcript details
        logger.info(f"Retrieved transcript with {len(fetched_transcript)} snippets")
        
        # Convert to different formats using formatters
        json_formatter = JSONFormatter()
        webvtt_formatter = WebVTTFormatter()
        
        # Save to files
        json_formatted = json_formatter.format_transcript(fetched_transcript, indent=2)
        webvtt_formatted = webvtt_formatter.format_transcript(fetched_transcript)
        
        file_prefix = f"{video_id}_transcript"
        
        with open(f"{file_prefix}.json", "w", encoding="utf-8") as f:
            f.write(json_formatted)
            logger.info(f"Saved transcript as JSON to {file_prefix}.json")
            
        with open(f"{file_prefix}.vtt", "w", encoding="utf-8") as f:
            f.write(webvtt_formatted)
            logger.info(f"Saved transcript as WebVTT to {file_prefix}.vtt")
            
        # Success!
        return True
            
    except Exception as e:
        logger.error(f"Error in advanced usage for video {video_id}: {str(e)}")
        logger.debug("Detailed traceback:", exc_info=True)
        return False


def main() -> None:
    """Main function to run the example script."""
    # Check command line arguments
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <scrapeops_api_key> [video_id1 video_id2 ...]")
        sys.exit(1)
        
    api_key = sys.argv[1]
    
    # Use provided video IDs or fall back to sample videos
    video_ids = sys.argv[2:] if len(sys.argv) > 2 else SAMPLE_VIDEOS
    
    print(f"Testing ScrapeOps integration with {len(video_ids)} video IDs")
    
    # Try each video ID until one works
    for video_id in video_ids:
        print(f"\nTrying video ID: {video_id}")
        
        # Try basic usage
        if basic_usage(video_id, api_key):
            print("\nBasic usage successful!")
            break
        else:
            print(f"Basic usage failed for video {video_id}, trying next video...")
    
    print("\n" + "-" * 50 + "\n")
    
    # Try each video ID until one works for advanced usage
    for video_id in video_ids:
        print(f"\nTrying advanced usage with video ID: {video_id}")
        
        # Try advanced usage
        if advanced_usage(video_id, api_key):
            print("\nAdvanced usage successful!")
            break
        else:
            print(f"Advanced usage failed for video {video_id}, trying next video...")


if __name__ == "__main__":
    main()