import os
from dotenv import load_dotenv
from anthropic import Anthropic, AsyncAnthropic, APIError

load_dotenv()

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

async def summarize_with_claude(content):
    client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    
    try:
        response = await client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4096,
            temperature=0.2,
            system="You are a precise and concise summarizer. Your summaries are in markdown list format, each point cited with a link to the source.",
            messages=[
                {"role": "user", "content": f"""Summarize the key takeaways from the following articles. 
                Provide only the main points in a markdown list, without any introductory text or concluding remarks. 
                Include a citation for each point, linking to the originating article in the following style: [Read](https://www.example.com/)
                Place the citation at the end of the point. 
                Be concise, direct, and ensure each point is substantive and informative:

                {content}"""},
                {"role": "assistant", "content": "Here are the key takeaways from the articles, in a markdown list with links:"}
            ]
        )
        return response.content[0].text.strip()
    except APIError as e:
        raise Exception(f"Anthropic API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error when calling Claude API: {str(e)}")

async def summarize_multiple(contents):
    summaries = []
    for content in contents:
        try:
            summary = await summarize_with_claude(content)
            summaries.append(summary)
        except Exception as e:
            summaries.append(f"Error summarizing content: {str(e)}")
    return summaries