from yfinance import Ticker
import yfinance as yf
import json


# reference https://github.com/ranaroussi/yfinance

def print_all_data(ticker_symbol, start_date, end_date):
    ticker = Ticker(ticker_symbol)

    # Last Month Stock Data
    #historical_data = ticker.history(period="1mo")

    # Historical data with specific start and end dates
    historical_data = ticker.history(start=start_date, end=end_date)
    print("Historical Data with Start/End Dates:")
    print(historical_data)

    # Financial Data
    financials = ticker.financials
    print("Financials:")
    print(financials)

    # Corporate
    actions = ticker.actions
    print("Stock Actions:")
    print(actions)

    news_items = ticker.news or []
    if not news_items:
        print("No news articles found.")
    else:
        print("News:")
        for news_article in news_items:
            print(json.dumps(news_article, indent=2, default=str))
            title = news_article.get("title")
            if not title:
                content = news_article.get("content")
                if isinstance(content, dict):
                    title = content.get("title")
            print(title or "Title not available")
            print("-" * 50)  # separator between articles



# Getting data for multiple tickers at once
def get_multiple_stocks_data(ticker_symbols, start_date, end_date):
    tickers_str = " ".join(ticker_symbols)
    data = yf.download(tickers_str, start=start_date, end=end_date)
    
    print(f"Historical data for {ticker_symbols}:")
    print(data)
    return data

# Example usage
ticker_list = ["AAPL", "GOOGL", "MSFT", "TSLA"]
print_all_data(ticker_list[0], "2025-09-01", "2025-10-01")

data = get_multiple_stocks_data(ticker_list, "2025-09-01", "2025-10-01")
if data is not None and "Close" in data and "TSLA" in data["Close"]:
    print(data["Close"]["TSLA"])
else:
    print("No data available for TSLA in the specified date range.")


