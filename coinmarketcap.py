# Import the Session helper from the requests library so we can make HTTP requests easily
from requests import Session
# Import specific exceptions to gracefully handle networking errors from requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
# Import json to decode the response body returned by CoinMarketCap
import json
# Import os to access environment variables such as the API key
import os


# Define a helper function that fetches the latest USD price for a given cryptocurrency ticker symbol
def get_latest_price(symbol):
    # Store the CoinMarketCap endpoint URL that provides the latest quotes
    api_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    # Read the CoinMarketCap API key from the COINMARKETCAP_API_KEY environment variable or fall back to the provided key
    api_key = os.getenv('COINMARKETCAP_API_KEY', '9ebde98563224475aa38a245b654ada7')
    # Ensure the API key exists before attempting the request, otherwise inform the user (protects against empty strings)
    if not api_key:
        raise ValueError('Missing API key: set COINMARKETCAP_API_KEY in your environment.')
    # Build the dictionary of parameters that tells the API which cryptocurrency we want data for
    request_parameters = {
        'symbol': symbol  # Pass the ticker symbol so the API knows which asset to look up
    }
    # Build the headers dictionary that includes the content type and our API key for authentication
    request_headers = {
        'Accepts': 'application/json',  # Tell the API that we want the response formatted as JSON
        'X-CMC_PRO_API_KEY': api_key,  # Include the API key (from env or fallback) required for authenticated access
    }
    # Create a reusable session object for making HTTP requests
    session = Session()
    # Attach our custom headers to the session so they are sent with every request
    session.headers.update(request_headers)
    # Attempt to call the CoinMarketCap API and parse the result
    try:
        # Send a GET request to the API endpoint with our parameters
        response = session.get(api_url, params=request_parameters)
        # Raise an HTTPError if the response status code indicates a failure
        response.raise_for_status()
        # Load the JSON response text into a Python dictionary for easier navigation
        parsed_data = json.loads(response.text)
        # Extract the USD price nested inside the JSON structure returned by CoinMarketCap
        price = parsed_data['data'][symbol]['quote']['USD']['price']
        # Return the extracted price so callers can use it
        return price
    except (ConnectionError, Timeout, TooManyRedirects) as api_error:
        # Print a helpful message if a network-related error occurs
        print(f'Request error: {api_error}')
        # Re-raise the exception so the calling code can decide how to handle it
        raise


# Run the following block when the script is executed directly
if __name__ == '__main__':
    # Choose the ticker symbol we want to look up, in this case Ethereum (ETH)
    target_symbol = 'ETH'
    # Try to retrieve the latest price and report the outcome
    try:
        # Call our helper function to get the latest price for the requested symbol
        latest_price = get_latest_price(target_symbol)
        # Print the formatted price to the terminal so we can verify the result quickly
        print(f'Latest {target_symbol} price: ${latest_price:.2f} USD')
    except Exception as general_error:
        # Inform the user if any part of the process failed
        print(f'Unable to fetch {target_symbol} price: {general_error}')
