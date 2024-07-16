import feedparser
import aiohttp
import asyncio
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os

from logging import getLogger
logger = getLogger(__name__)

def clean_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for img in soup.find_all('img'):
        img.decompose()
    
    for a in soup.find_all('a'):
        a.unwrap()
    
    text_content = soup.get_text()
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    
    return text_content

async def fetch_articles(feed_url, num_articles=20, cache_expiry=3600):
    cache_file = f"cache/{feed_url.replace('/', '_')}.json"
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cache = json.load(f)
        if datetime.now().timestamp() - cache['timestamp'] < cache_expiry:
            logger.info(f"Using cached data for {feed_url}")
            return cache['articles']

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(feed_url) as response:
                content = await response.text()
                feed = feedparser.parse(content)

            if not feed.entries:
                logger.error(f"No entries found in feed: {feed_url}")
                raise ValueError(f"No entries found in feed: {feed_url}")

            articles = []
            skipped_articles = 0
            for entry in feed.entries[:num_articles]:
                article_content = entry.get('content', [{'value': ''}])[0]['value']
                if not article_content:
                    logger.info(f"Skipping article '{entry.get('title')}' from {feed_url} due to lack of content")
                    skipped_articles += 1
                    continue
                
                cleaned_content = clean_content(article_content)
                article = {
                    'title': entry.get('title', 'No title'),
                    'link': entry.get('link', ''),
                    'content': cleaned_content,
                    'published': entry.get('published', 'Unknown date'),
                }
                articles.append(article)

            logger.info(f"Successfully fetched {len(articles)} articles from {feed_url}")
            if skipped_articles > 0:
                logger.warning(f"Skipped {skipped_articles} articles from {feed_url} due to lack of content")

            with open(cache_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().timestamp(),
                    'articles': articles
                }, f)

            return articles

        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}")
            raise ValueError(f"Error fetching feed {feed_url}: {e}")

async def fetch_all_feeds(feed_urls, articles_per_feed=20, cache_expiry=3600):
    async def fetch_with_url(url):
        try:
            articles = await fetch_articles(url, articles_per_feed, cache_expiry)
            feed = feedparser.parse(url)
            feed_title = feed.feed.get('title', 'Unknown Feed')
            logger.info(f"Fetched {len(articles)} articles for feed: {feed_title}")
            return (url, feed_title, articles)
        except Exception as e:
            logger.error(f"Error fetching feed {url}: {e}")
            return (url, 'Unknown Feed', e)

    tasks = [fetch_with_url(url) for url in feed_urls]
    results = await asyncio.gather(*tasks)
    
    valid_results = [(url, title, articles) for url, title, articles in results if isinstance(articles, list) and articles]
    
    skipped_feeds = len(results) - len(valid_results)
    if skipped_feeds > 0:
        logger.warning(f"Skipped {skipped_feeds} feed(s) due to errors or lack of content")
    
    return valid_results