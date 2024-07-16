import os
from dotenv import load_dotenv

def get_config():
    load_dotenv()
    
    required_params = ['GITHUB_TOKEN', 'GITHUB_REPO', 'ANTHROPIC_API_KEY']
    
    config = {}
    for param in required_params:
        value = os.getenv(param)
        if value is None:
            raise ValueError(f"Missing required configuration parameter: {param}")
        config[param] = value
    
    config['ARTICLES_PER_FEED'] = int(os.getenv('ARTICLES_PER_FEED', 20))
    config['ARTICLES_PER_BATCH'] = int(os.getenv('ARTICLES_PER_BATCH', 10))
    config['CACHE_EXPIRY'] = int(os.getenv('CACHE_EXPIRY', 3600))  # Cache expiry in seconds, default 1 hour
    
    return config