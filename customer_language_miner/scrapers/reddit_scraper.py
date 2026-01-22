"""Reddit scraper for customer language mining."""

import praw
from typing import List, Dict, Optional
import time
from datetime import datetime


class RedditScraper:
    """Scrapes customer language from Reddit threads and comments."""

    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize Reddit scraper.

        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string for Reddit API
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def scrape_subreddit(
        self,
        subreddit_name: str,
        query: str,
        limit: int = 100,
        time_filter: str = "month"
    ) -> List[Dict]:
        """
        Scrape posts and comments from a subreddit.

        Args:
            subreddit_name: Name of the subreddit to scrape
            query: Search query for finding relevant posts
            limit: Maximum number of posts to retrieve
            time_filter: Time filter (hour, day, week, month, year, all)

        Returns:
            List of dictionaries containing post and comment data
        """
        results = []
        subreddit = self.reddit.subreddit(subreddit_name)

        try:
            # Search for relevant posts
            for submission in subreddit.search(query, limit=limit, time_filter=time_filter):
                post_data = {
                    'source': 'reddit',
                    'subreddit': subreddit_name,
                    'post_id': submission.id,
                    'title': submission.title,
                    'text': submission.selftext,
                    'author': str(submission.author),
                    'score': submission.score,
                    'created_utc': datetime.fromtimestamp(submission.created_utc).isoformat(),
                    'num_comments': submission.num_comments,
                    'url': f"https://reddit.com{submission.permalink}",
                    'comments': []
                }

                # Get top comments
                submission.comment_sort = 'top'
                submission.comments.replace_more(limit=0)  # Remove "more comments" objects

                for comment in submission.comments.list()[:20]:  # Top 20 comments
                    if hasattr(comment, 'body') and comment.body:
                        comment_data = {
                            'text': comment.body,
                            'author': str(comment.author),
                            'score': comment.score,
                            'created_utc': datetime.fromtimestamp(comment.created_utc).isoformat()
                        }
                        post_data['comments'].append(comment_data)

                results.append(post_data)
                time.sleep(1)  # Rate limiting

        except Exception as e:
            print(f"Error scraping r/{subreddit_name}: {str(e)}")

        return results

    def scrape_multiple_subreddits(
        self,
        subreddits: List[str],
        query: str,
        limit_per_subreddit: int = 50
    ) -> List[Dict]:
        """
        Scrape multiple subreddits with the same query.

        Args:
            subreddits: List of subreddit names
            query: Search query
            limit_per_subreddit: Max posts per subreddit

        Returns:
            Combined list of results from all subreddits
        """
        all_results = []

        for subreddit in subreddits:
            print(f"Scraping r/{subreddit}...")
            results = self.scrape_subreddit(subreddit, query, limit_per_subreddit)
            all_results.extend(results)
            time.sleep(2)  # Rate limiting between subreddits

        return all_results

    def get_post_details(self, post_url: str) -> Optional[Dict]:
        """
        Get detailed information about a specific post.

        Args:
            post_url: URL or ID of the Reddit post

        Returns:
            Dictionary containing post details
        """
        try:
            submission = self.reddit.submission(url=post_url)
            return {
                'source': 'reddit',
                'post_id': submission.id,
                'title': submission.title,
                'text': submission.selftext,
                'author': str(submission.author),
                'score': submission.score,
                'created_utc': datetime.fromtimestamp(submission.created_utc).isoformat(),
                'url': f"https://reddit.com{submission.permalink}"
            }
        except Exception as e:
            print(f"Error fetching post details: {str(e)}")
            return None
