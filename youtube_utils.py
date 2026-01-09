"""
YouTube utilities for extracting video IDs and thumbnail URLs.
"""

import re
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class YouTubeExtractor:
    """Handles YouTube video ID extraction and thumbnail generation."""
    
    # Various YouTube URL patterns
    PATTERNS = [
        # Standard watch URL
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        # Short URL
        r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',
        # Embed URL
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        # YouTube Shorts
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        # YouTube Live
        r'(?:https?://)?(?:www\.)?youtube\.com/live/([a-zA-Z0-9_-]{11})',
        # v= parameter anywhere in URL
        r'[?&]v=([a-zA-Z0-9_-]{11})',
        # Just the video ID (11 characters)
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    
    @staticmethod
    def extract_video_id(text: str) -> Optional[str]:
        """
        Extract YouTube video ID from various URL formats or plain ID.
        
        Args:
            text: URL or video ID string
            
        Returns:
            Video ID if found, None otherwise
        """
        text = text.strip()
        
        for pattern in YouTubeExtractor.PATTERNS:
            match = re.search(pattern, text)
            if match:
                video_id = match.group(1)
                logger.info(f"Extracted video ID: {video_id}")
                return video_id
        
        logger.warning(f"Could not extract video ID from: {text}")
        return None
    
    @staticmethod
    def get_thumbnails(video_id: str) -> List[Dict[str, str]]:
        """
        Generate all available thumbnail URLs for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of dictionaries with quality and URL
        """
        thumbnails = [
            {
                'quality': 'Maximum Resolution (1920x1080)',
                'url': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
                'filename': f'{video_id}_maxres.jpg'
            },
            {
                'quality': 'Standard Definition (640x480)',
                'url': f'https://img.youtube.com/vi/{video_id}/sddefault.jpg',
                'filename': f'{video_id}_sd.jpg'
            },
            {
                'quality': 'High Quality (480x360)',
                'url': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
                'filename': f'{video_id}_hq.jpg'
            },
            {
                'quality': 'Medium Quality (320x180)',
                'url': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg',
                'filename': f'{video_id}_mq.jpg'
            },
            {
                'quality': 'Default (120x90)',
                'url': f'https://img.youtube.com/vi/{video_id}/default.jpg',
                'filename': f'{video_id}_default.jpg'
            },
            {
                'quality': 'Thumbnail 1',
                'url': f'https://img.youtube.com/vi/{video_id}/1.jpg',
                'filename': f'{video_id}_1.jpg'
            },
            {
                'quality': 'Thumbnail 2',
                'url': f'https://img.youtube.com/vi/{video_id}/2.jpg',
                'filename': f'{video_id}_2.jpg'
            },
            {
                'quality': 'Thumbnail 3',
                'url': f'https://img.youtube.com/vi/{video_id}/3.jpg',
                'filename': f'{video_id}_3.jpg'
            },
        ]
        
        logger.info(f"Generated {len(thumbnails)} thumbnail URLs for video {video_id}")
        return thumbnails
    
    @staticmethod
    def validate_video_id(video_id: str) -> bool:
        """
        Validate if a string is a valid YouTube video ID format.
        
        Args:
            video_id: String to validate
            
        Returns:
            True if valid format, False otherwise
        """
        if not video_id:
            return False
        
        # YouTube video IDs are exactly 11 characters, alphanumeric with - and _
        pattern = r'^[a-zA-Z0-9_-]{11}$'
        return bool(re.match(pattern, video_id))
