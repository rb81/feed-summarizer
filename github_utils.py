import os
from github import Github
from github.GithubException import GithubException
from dotenv import load_dotenv

from logging import getLogger
logger = getLogger(__name__)

load_dotenv()

def connect_to_github(token=None):
    if token is None:
        token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        raise ValueError("GitHub token not provided and not found in environment variables.")
    
    try:
        g = Github(token)
        user = g.get_user()
        logger.info(f"Successfully connected to GitHub as {user.login}")
        return g
    except GithubException as e:
        logger.error(f"GitHub authentication failed: {e}")
        raise

def get_repo(github_connection, repo_name):
    try:
        repo = github_connection.get_repo(repo_name)
        logger.info(f"Successfully retrieved repository: {repo_name}")
        return repo
    except GithubException as e:
        if e.status == 404:
            raise ValueError(f"Repository not found: {repo_name}")
        else:
            logger.error(f"Error accessing repository {repo_name}: {e}")
            raise

def get_feed_urls(repo, file_path='feeds.txt'):
    try:
        file_content = repo.get_contents(file_path)
        content = file_content.decoded_content.decode('utf-8')
        urls = [url.strip() for url in content.split('\n') if url.strip()]
        
        if not urls:
            raise ValueError(f"No valid URLs found in {file_path}")
        
        logger.info(f"Successfully retrieved {len(urls)} feed URLs from {file_path}")
        return urls
    
    except GithubException as e:
        if e.status == 404:
            raise ValueError(f"File not found: {file_path}")
        else:
            logger.error(f"Error accessing file {file_path}: {e}")
            raise

def commit_file_to_repo(repo, file_content, file_path, commit_message, branch_name="main"):
    try:
        try:
            contents = repo.get_contents(file_path, ref=branch_name)
            repo.update_file(contents.path, commit_message, file_content, contents.sha, branch=branch_name)
            logger.info(f"Updated existing file: {file_path}")
        except GithubException as e:
            if e.status == 404:
                repo.create_file(file_path, commit_message, file_content, branch=branch_name)
                logger.info(f"Created new file: {file_path}")
            else:
                raise

        file_url = f"https://github.com/{repo.full_name}/blob/{branch_name}/{file_path}"
        logger.info(f"Successfully committed file to {file_url}")
        return file_url

    except GithubException as e:
        logger.error(f"Error committing to repository: {e}")
        raise

def create_or_update_folder(repo, folder_path, branch_name="main"):
    try:
        try:
            repo.get_contents(folder_path, ref=branch_name)
            logger.info(f"Folder already exists: {folder_path}")
        except GithubException as e:
            if e.status == 404:
                repo.create_file(f"{folder_path}/.gitkeep", f"Create folder: {folder_path}", "", branch=branch_name)
                logger.info(f"Created new folder: {folder_path}")
            else:
                raise

    except GithubException as e:
        logger.error(f"Error creating folder in repository: {e}")
        raise