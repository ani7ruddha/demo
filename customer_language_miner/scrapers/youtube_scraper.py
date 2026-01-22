"""YouTube comments scraper for customer language mining."""

from typing import List, Dict, Optional
from googleapiclient.discovery import build
from datetime import datetime
import time


class YouTubeScraper:
    """Scrapes comments from YouTube videos."""

    def __init__(self, api_key: str):
        """
        Initialize YouTube scraper.

        Args:
            api_key: YouTube Data API v3 key
        """
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.api_key = api_key

    def scrape_video_comments(
        self,
        video_id: str,
        max_comments: int = 100,
        order: str = 'relevance'
    ) -> List[Dict]:
        """
        Scrape comments from a specific YouTube video.

        Args:
            video_id: YouTube video ID
            max_comments: Maximum number of comments to retrieve
            order: Order of comments ('time', 'relevance')

        Returns:
            List of comment dictionaries
        """
        comments = []
        next_page_token = None

        try:
            while len(comments) < max_comments:
                request = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=min(100, max_comments - len(comments)),
                    order=order,
                    pageToken=next_page_token,
                    textFormat='plainText'
                )

                response = request.execute()

                for item in response.get('items', []):
                    top_comment = item['snippet']['topLevelComment']['snippet']

                    comment_data = {
                        'source': 'youtube',
                        'video_id': video_id,
                        'comment_id': item['id'],
                        'text': top_comment['textDisplay'],
                        'author': top_comment['authorDisplayName'],
                        'author_channel_id': top_comment.get('authorChannelId', {}).get('value', ''),
                        'like_count': top_comment['likeCount'],
                        'published_at': top_comment['publishedAt'],
                        'updated_at': top_comment['updatedAt'],
                        'reply_count': item['snippet']['totalReplyCount'],
                        'replies': []
                    }

                    # Get replies if available
                    if item['snippet']['totalReplyCount'] > 0:
                        comment_data['replies'] = self._get_comment_replies(
                            item['id'],
                            max_replies=5
                        )

                    comments.append(comment_data)

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

                time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"Error scraping video comments: {str(e)}")

        return comments

    def _get_comment_replies(self, parent_id: str, max_replies: int = 5) -> List[Dict]:
        """
        Get replies to a comment.

        Args:
            parent_id: ID of the parent comment
            max_replies: Maximum number of replies to retrieve

        Returns:
            List of reply dictionaries
        """
        replies = []

        try:
            request = self.youtube.comments().list(
                part='snippet',
                parentId=parent_id,
                maxResults=max_replies,
                textFormat='plainText'
            )

            response = request.execute()

            for item in response.get('items', []):
                snippet = item['snippet']
                reply_data = {
                    'text': snippet['textDisplay'],
                    'author': snippet['authorDisplayName'],
                    'like_count': snippet['likeCount'],
                    'published_at': snippet['publishedAt']
                }
                replies.append(reply_data)

        except Exception as e:
            print(f"Error getting replies: {str(e)}")

        return replies

    def search_videos(
        self,
        query: str,
        max_results: int = 10,
        order: str = 'relevance'
    ) -> List[Dict]:
        """
        Search for YouTube videos by query.

        Args:
            query: Search query
            max_results: Maximum number of videos to return
            order: Sort order ('date', 'rating', 'relevance', 'viewCount')

        Returns:
            List of video information dictionaries
        """
        videos = []

        try:
            request = self.youtube.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=max_results,
                order=order
            )

            response = request.execute()

            for item in response.get('items', []):
                video_data = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail_url': item['snippet']['thumbnails']['default']['url']
                }
                videos.append(video_data)

        except Exception as e:
            print(f"Error searching videos: {str(e)}")

        return videos

    def scrape_search_comments(
        self,
        query: str,
        max_videos: int = 5,
        comments_per_video: int = 50
    ) -> List[Dict]:
        """
        Search for videos and scrape comments from them.

        Args:
            query: Search query for videos
            max_videos: Number of videos to scrape
            comments_per_video: Number of comments per video

        Returns:
            Combined list of comments from all videos
        """
        print(f"Searching for videos matching: {query}")
        videos = self.search_videos(query, max_results=max_videos)

        all_comments = []
        for i, video in enumerate(videos, 1):
            video_id = video['video_id']
            print(f"Scraping video {i}/{len(videos)}: {video['title']}")

            comments = self.scrape_video_comments(video_id, max_comments=comments_per_video)

            # Add video metadata to each comment
            for comment in comments:
                comment['video_title'] = video['title']
                comment['video_url'] = f"https://www.youtube.com/watch?v={video_id}"
                comment['channel_title'] = video['channel_title']

            all_comments.extend(comments)
            time.sleep(1)  # Rate limiting between videos

        return all_comments

    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary containing video details
        """
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            )

            response = request.execute()

            if response.get('items'):
                item = response['items'][0]
                snippet = item['snippet']
                statistics = item['statistics']

                return {
                    'video_id': video_id,
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'channel_title': snippet['channelTitle'],
                    'published_at': snippet['publishedAt'],
                    'view_count': int(statistics.get('viewCount', 0)),
                    'like_count': int(statistics.get('likeCount', 0)),
                    'comment_count': int(statistics.get('commentCount', 0))
                }

        except Exception as e:
            print(f"Error getting video details: {str(e)}")

        return None
