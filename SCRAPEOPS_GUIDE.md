# Using YouTube Transcript API with ScrapeOps

This guide explains how to use the ScrapeOps integration with the YouTube Transcript API to reliably retrieve transcripts from YouTube videos.

## What is ScrapeOps?

[ScrapeOps](https://scrapeops.io/) is a proxy provider service that helps overcome common scraping challenges:

- IP blocks and rate limiting
- CAPTCHA and bot detection
- JavaScript rendering
- Geolocation-specific content

## Installation

First, install the YouTube Transcript API:

```bash
pip install youtube-transcript-api
```

## Getting a ScrapeOps API Key

1. Sign up for a ScrapeOps account at [https://scrapeops.io/](https://scrapeops.io/)
2. After signing up, navigate to your dashboard and find your API key
3. Note your API key for use in your code

## Basic Usage

Here's a simple example of using the ScrapeOps integration:

```python
from youtube_transcript_api import YouTubeTranscriptApi

# Initialize the API with your ScrapeOps API key
ytt_api = YouTubeTranscriptApi(scrapeops_api_key="YOUR_SCRAPEOPS_API_KEY")

# Fetch a transcript
video_id = "VIDEO_ID"  # e.g., "dQw4w9WgXcQ"
transcript = ytt_api.fetch(video_id)

# Print the transcript
for snippet in transcript:
    print(f"[{snippet.start:.1f}s]: {snippet.text}")
```

## Advanced Usage

For more control, you can create a custom ScrapeOpsClient:

```python
from youtube_transcript_api import YouTubeTranscriptApi, ScrapeOpsClient

# Create a custom ScrapeOps client
scrapeops_client = ScrapeOpsClient(
    api_key="YOUR_SCRAPEOPS_API_KEY",
    timeout=180  # Custom timeout in seconds
)

# Add custom headers if needed
scrapeops_client.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
})

# Use the client with YouTubeTranscriptApi
ytt_api = YouTubeTranscriptApi(http_client=scrapeops_client)

# Now use the API as usual
transcript = ytt_api.fetch(video_id)
```

## Combining with Cookie Authentication

For age-restricted videos, you can combine ScrapeOps with cookie authentication:

```python
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi, ScrapeOpsClient

# Create a ScrapeOps client
scrapeops_client = ScrapeOpsClient(api_key="YOUR_SCRAPEOPS_API_KEY")

# Initialize API with both ScrapeOps and cookies
ytt_api = YouTubeTranscriptApi(
    http_client=scrapeops_client,
    cookie_path=Path("/path/to/cookies.txt")
)

# Now you can access age-restricted videos
transcript = ytt_api.fetch(video_id)
```

## Command Line Usage

You can also use ScrapeOps with the CLI tool:

```bash
youtube_transcript_api VIDEO_ID --scrapeops-api-key YOUR_API_KEY
```

For age-restricted videos with cookies:

```bash
youtube_transcript_api VIDEO_ID --scrapeops-api-key YOUR_API_KEY --cookies /path/to/cookies.txt
```

## Example Scripts

The following example scripts are included to demonstrate ScrapeOps integration:

- `example_scrapeops.py`: Basic and advanced usage examples
- `example_batch_processing.py`: Process multiple videos in parallel
- `example_age_restricted.py`: Handling age-restricted videos

## Troubleshooting

If you encounter issues:

1. **Check your API key**: Ensure your ScrapeOps API key is valid and correctly entered
2. **Check your plan limits**: Ensure you haven't exceeded your ScrapeOps plan limits
3. **Try with cookies**: For age-restricted content, YouTube cookies are required
4. **Add delays between requests**: Add small delays between requests to avoid triggering rate limits

## Best Practices

1. **Use appropriate timeouts**: YouTube transcripts can take time to load; use a longer timeout (60-180 seconds)
2. **Add browser-like headers**: Make your requests look more like a real browser
3. **Handle errors gracefully**: Implement proper error handling for various failure scenarios
4. **Consider rate limiting**: Add delays between requests, especially when processing multiple videos
5. **Use appropriate language parameters**: Specify multiple language options in decreasing order of preference
