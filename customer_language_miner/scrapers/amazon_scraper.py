"""Amazon reviews scraper for customer language mining."""

from typing import List, Dict, Optional
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


class AmazonScraper:
    """Scrapes customer reviews from Amazon product pages."""

    def __init__(self, headers: Optional[Dict] = None):
        """
        Initialize Amazon scraper.

        Args:
            headers: Optional custom headers for requests
        """
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def scrape_product_reviews(
        self,
        product_asin: str,
        max_pages: int = 5,
        star_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Scrape reviews for a specific Amazon product.

        Args:
            product_asin: Amazon Standard Identification Number (ASIN) of the product
            max_pages: Maximum number of review pages to scrape
            star_filter: Filter by star rating (e.g., 'one_star', 'two_star', etc.)

        Returns:
            List of review dictionaries
        """
        reviews = []
        base_url = f"https://www.amazon.com/product-reviews/{product_asin}/ref=cm_cr_arp_d_viewopt_sr"

        for page in range(1, max_pages + 1):
            params = {
                'pageNumber': page,
                'sortBy': 'recent'
            }

            if star_filter:
                params['filterByStar'] = star_filter

            try:
                response = self.session.get(base_url, params=params, timeout=30)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')
                review_elements = soup.find_all('div', {'data-hook': 'review'})

                if not review_elements:
                    print(f"No reviews found on page {page}")
                    break

                for review in review_elements:
                    review_data = self._parse_review(review, product_asin)
                    if review_data:
                        reviews.append(review_data)

                print(f"Scraped page {page}/{max_pages} - Found {len(review_elements)} reviews")
                time.sleep(2)  # Rate limiting

            except Exception as e:
                print(f"Error scraping page {page}: {str(e)}")
                break

        return reviews

    def _parse_review(self, review_element, product_asin: str) -> Optional[Dict]:
        """
        Parse a single review element.

        Args:
            review_element: BeautifulSoup element containing review
            product_asin: Product ASIN

        Returns:
            Dictionary containing review data
        """
        try:
            # Extract review ID
            review_id = review_element.get('id', '')

            # Extract rating
            rating_element = review_element.find('i', {'data-hook': 'review-star-rating'})
            rating = None
            if rating_element:
                rating_text = rating_element.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))

            # Extract title
            title_element = review_element.find('a', {'data-hook': 'review-title'})
            title = title_element.get_text(strip=True) if title_element else ''

            # Extract review text
            text_element = review_element.find('span', {'data-hook': 'review-body'})
            text = text_element.get_text(strip=True) if text_element else ''

            # Extract author
            author_element = review_element.find('span', {'class': 'a-profile-name'})
            author = author_element.get_text(strip=True) if author_element else 'Anonymous'

            # Extract date
            date_element = review_element.find('span', {'data-hook': 'review-date'})
            date = date_element.get_text(strip=True) if date_element else ''

            # Extract helpful count
            helpful_element = review_element.find('span', {'data-hook': 'helpful-vote-statement'})
            helpful_count = 0
            if helpful_element:
                helpful_text = helpful_element.get_text(strip=True)
                helpful_match = re.search(r'(\d+)', helpful_text)
                if helpful_match:
                    helpful_count = int(helpful_match.group(1))

            # Extract verified purchase status
            verified = bool(review_element.find('span', {'data-hook': 'avp-badge'}))

            return {
                'source': 'amazon',
                'product_asin': product_asin,
                'review_id': review_id,
                'title': title,
                'text': text,
                'rating': rating,
                'author': author,
                'date': date,
                'helpful_count': helpful_count,
                'verified_purchase': verified,
                'scraped_at': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error parsing review: {str(e)}")
            return None

    def scrape_search_results(self, search_query: str, max_products: int = 10) -> List[str]:
        """
        Search Amazon and get product ASINs.

        Args:
            search_query: Search query for products
            max_products: Maximum number of product ASINs to return

        Returns:
            List of product ASINs
        """
        asins = []
        url = "https://www.amazon.com/s"
        params = {'k': search_query}

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            product_elements = soup.find_all('div', {'data-asin': True})

            for element in product_elements[:max_products]:
                asin = element.get('data-asin')
                if asin and len(asin) == 10:  # Valid ASIN length
                    asins.append(asin)

        except Exception as e:
            print(f"Error searching Amazon: {str(e)}")

        return asins

    def scrape_category_reviews(
        self,
        search_query: str,
        max_products: int = 5,
        reviews_per_product: int = 20
    ) -> List[Dict]:
        """
        Scrape reviews from multiple products in a category.

        Args:
            search_query: Product category or search term
            max_products: Number of products to scrape
            reviews_per_product: Number of reviews per product

        Returns:
            Combined list of reviews from all products
        """
        print(f"Searching for products matching: {search_query}")
        asins = self.scrape_search_results(search_query, max_products)

        all_reviews = []
        for i, asin in enumerate(asins, 1):
            print(f"Scraping product {i}/{len(asins)} (ASIN: {asin})")
            reviews = self.scrape_product_reviews(asin, max_pages=reviews_per_product // 10)
            all_reviews.extend(reviews)
            time.sleep(3)  # Rate limiting between products

        return all_reviews
