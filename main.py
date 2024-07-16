import asyncio
from datetime import datetime
from config_utils import get_config
from github_utils import connect_to_github, get_repo, get_feed_urls, commit_file_to_repo, create_or_update_folder
from feed_utils import fetch_all_feeds
from claude_utils import summarize_multiple
from logging import getLogger, INFO
from logging_utils import setup_logging

logger = setup_logging(console_level=INFO)

def create_markdown_content(feed_title, articles):
    content = f"# {feed_title}\n\n"
    for article in articles:
        content += f"## {article['title']}\n"
        content += f"{article['link']}\n\n"
        content += f"Published: {article['published']}\n\n"
        content += f"{article['content']}\n\n"
        content += "---\n\n"
    return content

async def process_feed(repo, feed_url, feed_title, articles, date, articles_per_batch):
    folder_path = f"feed_summaries/{date}"
    create_or_update_folder(repo, folder_path)
    
    num_files = (len(articles) - 1) // articles_per_batch + 1
    logger.info(f"Processing feed: {feed_title}")
    logger.info(f"Total articles: {len(articles)}")
    logger.info(f"Articles per batch: {articles_per_batch}")
    logger.info(f"Number of files to create: {num_files}")
    
    file_urls = []
    contents = []

    for i in range(num_files):
        start = i * articles_per_batch
        end = min((i + 1) * articles_per_batch, len(articles))
        file_name = f"{date}-{feed_title.lower().replace(' ', '-')}-{i+1:02d}.md"
        file_path = f"{folder_path}/{file_name}"
        
        logger.info(f"Creating file {i+1} of {num_files}: {file_name}")
        logger.info(f"Articles range: {start} to {end}")
        
        content = create_markdown_content(feed_title, articles[start:end])
        contents.append(content)
        
        commit_message = f"Add/Update summary for {feed_title} (Part {i+1:02d}) on {date}"
        file_url = commit_file_to_repo(repo, content.strip(), file_path, commit_message)
        file_urls.append((file_name, file_url))
    
    logger.info(f"Finished processing feed: {feed_title}")
    logger.info(f"Files created: {len(file_urls)}")
    return file_urls, contents

async def main():
    try:
        config = get_config()
        logger.info("Configuration loaded successfully")
        logger.info(f"ARTICLES_PER_FEED: {config['ARTICLES_PER_FEED']}")
        logger.info(f"ARTICLES_PER_BATCH: {config['ARTICLES_PER_BATCH']}")

        github_connection = connect_to_github(config['GITHUB_TOKEN'])
        repo = get_repo(github_connection, config['GITHUB_REPO'])
        logger.info(f"Connected to GitHub repository: {config['GITHUB_REPO']}")

        feed_urls = get_feed_urls(repo)
        logger.info(f"Retrieved {len(feed_urls)} feed URLs")

        current_date = datetime.now().strftime("%Y-%m-%d")

        all_articles = await fetch_all_feeds(feed_urls, config['ARTICLES_PER_FEED'], config['CACHE_EXPIRY'])
        logger.info(f"Fetched articles from {len(all_articles)} feeds")

        all_summaries = []
        all_contents = []
        for feed_url, feed_title, articles in all_articles:
            if isinstance(articles, Exception):
                logger.error(f"Error processing feed {feed_url}: {articles}")
                continue
            
            logger.info(f"Processing feed: {feed_title}")
            logger.info(f"Number of articles fetched: {len(articles)}")
            
            feed_summaries, feed_contents = await process_feed(repo, feed_url, feed_title, articles, current_date, config['ARTICLES_PER_BATCH'])
            all_summaries.extend(feed_summaries)
            all_contents.extend(feed_contents)

        logger.info("Summarizing content with Claude")
        claude_summaries = await summarize_multiple(all_contents)

        daily_summary_content = f"# RSS Feed Summaries for {current_date}\n\n"
        for (file_name, file_url), claude_summary in zip(all_summaries, claude_summaries):
            daily_summary_content += f"## [{file_name}]({file_url})\n\n"
            daily_summary_content += f"Key takeaways:\n{claude_summary}\n\n"
            daily_summary_content += "---\n\n"

        daily_summary_folder = f"daily_summaries/{current_date[:4]}/{current_date[5:7]}"
        create_or_update_folder(repo, daily_summary_folder)
        daily_summary_path = f"{daily_summary_folder}/rss-summary-{current_date}.md"
        daily_summary_commit_message = f"Add daily RSS summary for {current_date}"
        daily_summary_url = commit_file_to_repo(repo, daily_summary_content, daily_summary_path, daily_summary_commit_message)

        logger.info(f"Daily summary committed to: {daily_summary_url}")
        print(f"RSS feed summaries for {current_date} have been generated and committed.")
        print(f"You can view the daily summary at: {daily_summary_url}")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        print(f"An error occurred. Please check the log file for details.")

if __name__ == "__main__":
    asyncio.run(main())