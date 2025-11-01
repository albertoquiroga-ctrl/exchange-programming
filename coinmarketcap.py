from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json


def get_latest_price(symbol):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': symbol
    }
    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': 'your-key-here',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        return data["data"][symbol]["quote"]["USD"]["price"]
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)