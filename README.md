# Feed Summarizer

![Feed Summarizer](/header.png)

Feed Summarizer is a Python application that aggregates articles from multiple RSS feeds, summarizes them using the Anthropic Claude API, and stores the results in a GitHub repository.

## Features

- Fetches articles from multiple RSS feeds
- Summarizes articles using Anthropic's Claude AI
- Caches feed data to reduce API calls
- Stores summaries in a GitHub repository
- Configurable via environment variables
- Generates daily summaries of all processed feeds

## Prerequisites

- Python 3.7+
- GitHub account and personal access token
- Anthropic API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/rb81/feed-summarizer.git
   cd feed-summarizer
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root with the following content:
   ```
   GITHUB_TOKEN=your_github_token
   GITHUB_REPO=your_username/your_repo_name
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ARTICLES_PER_FEED=20
   ARTICLES_PER_BATCH=10
   CACHE_EXPIRY=3600
   ```

## Usage

1. Add your RSS feed URLs to a `feeds.txt` file in your GitHub repository, one URL per line.

2. Run the main script:
   ```
   python main.py
   ```

The script will fetch articles from the specified feeds, summarize them using Claude, and commit the summaries to your GitHub repository. It will also generate a daily summary of all processed feeds.

## Configuration

You can adjust the following settings in your `.env` file:

- `ARTICLES_PER_FEED`: Number of articles to fetch per feed (default: 20)
- `ARTICLES_PER_BATCH`: Number of articles to summarize in each batch (default: 10)
- `CACHE_EXPIRY`: Cache expiry time in seconds (default: 3600)

## Project Structure

- `main.py`: The main script that orchestrates the entire process
- `claude_utils.py`: Handles interaction with the Anthropic API for summarization
- `config_utils.py`: Manages configuration and environment variables
- `feed_utils.py`: Fetches and processes RSS feeds
- `github_utils.py`: Handles GitHub repository operations
- `logging_utils.py`: Sets up logging for the application

## Considerations

- This application skips feeds that do not include content. You can add functionality to scrape or pull content from the relevant websites in such cases.
- Be aware of the fact that this application may consume a substantial number of tokens if summarizing larger collections of feeds.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Transparency Disclaimer

[ai.collaboratedwith.me](https://ai.collaboratedwith.me) in creating this project.
