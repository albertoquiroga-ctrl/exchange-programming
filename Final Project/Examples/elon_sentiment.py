import requests
import time
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key = "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"
)

def sentiment_analysis(client, message):
	prompt = "Evaluate whether there are very positive, positive, neutral, negative, very negative that text on the impact to stock market. Only output one of the following very positive, positive, neutral, negative, very negative"
	completion = client.chat.completions.create(
			model="meta-llama/llama-3.1-405b-instruct:free",
			messages=[
			  {
				  "role": "user", "content": message + prompt,
			  }
			]
	)
	return completion.choices[0].message.content



def tweet_sentiment(client, screen_name):
	url = "https://twitter-api45.p.rapidapi.com/timeline.php"

	querystring = {"screenname":screen_name}

	headers = {
		"x-rapidapi-key": "530a96e66cmshfa7b24b93c96ea6p1791b7jsn6a5526041c4c",
		"x-rapidapi-host": "twitter-api45.p.rapidapi.com"
	}

	response = requests.get(url, headers=headers, params=querystring)

	data = response.json()
	for tweet in data["timeline"]:
		print("++++++++++++++++++++++")
		print(tweet["text"])
		try:
			print(sentiment_analysis(client, tweet["text"]))
		except TypeError:
			print("Error in sentiment analysis")
		time.sleep(62)


tweet_sentiment(client, "elonmusk")