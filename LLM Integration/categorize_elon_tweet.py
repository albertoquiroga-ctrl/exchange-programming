import requests
import time
from open_router_client import ask_open_router

def gen_prompt(content):
    return f'''
        You are an expert annotator analyzing individual tweets by Elon Musk.

Tweet:
{content}

Your tasks:

1. Assign the tweet to exactly ONE of the following categories (choose the best fit):
   - "Tesla"                  – anything about Tesla, its products, stock, management, factories, etc.
   - "SpaceX"                 – rockets, Starship, Starlink, launches, satellites, etc.
   - "X"                      – X (formerly Twitter), product features, policies, moderation, company issues.
   - "xAI / Grok"             – xAI, Grok, AI model capabilities, AI safety comments tied to xAI.
   - "Other Elon Musk Company"– Neuralink, The Boring Company, SolarCity, OpenAI (historical), or other Musk ventures not covered above.
   - "US Politics"            – US government, elections, US politicians, US political parties, US public policy.
   - "Global Politics"        – non-US governments, geopolitics, wars, diplomacy, global policy issues.
   - "Cryptocurrency"         – Bitcoin, Dogecoin, other coins, crypto markets, blockchain talk.
   - "Fun or Entertainment"   – memes, jokes, casual banter, movies, games, random internet fun.
   - "Freedom of Speech"      - Anything related to fighting freedom of speech
   - "Other / General"        – anything that doesn’t clearly fit into the above (e.g. personal reflections, generic tech talk, random comments).

2. Determine the sentiment of the tweet **within that category**:
   - "positive"
   - "negative"
   - "neutral"

Guidelines:
- Base your decision ONLY on the tweet content provided.
- If the tweet seems to touch multiple areas, pick the **single most central** topic.
- Consider sarcasm or jokes when inferring sentiment, but do not over-interpret beyond what is reasonable from the text.

Output **only** valid JSON in this format:

{{
  "category": "<one of the categories above>",
  "sentiment": "positive" | "negative" | "neutral",
  "reason": "<very short explanation of why you chose this category and sentiment>"
}}
    '''



url = "https://twitter241.p.rapidapi.com/user-tweets"

querystring = {"user":"44196397","count":"20"}

headers = {
	"x-rapidapi-key": "3cd811471cmsh7102d1f81e51a80p140b13jsnb18dbf2fecaa",
	"x-rapidapi-host": "twitter241.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

data = response.json()

posts = data['result']['timeline']['instructions'][-1]["entries"]


for post in posts:
    try:
        content = post['content']['itemContent']['tweet_results']['result']['legacy']['full_text']
        prompt = gen_prompt(content)
        result = ask_open_router(prompt)
        print(content)
        print(f"LLM Response: {result}")
        print("-" * 40)
    except KeyError as e:
        pass
        #print(f"Error getting twitter content: {e}")
    except Exception as e:
        pass
        #print(f"Error while categorizing tweet: {e}")

    time.sleep(10)


