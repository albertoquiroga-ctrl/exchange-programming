import yfinance as yf
import pandas as pd
from pypfopt import EfficientFrontier, risk_models, expected_returns, objective_functions

def portfolio_optimization(tickers, train_period, test_period, max_weight=0.20, risk_free_rate=0.03):
    """
    Optimize a portfolio based on training data and evaluate its performance on testing data.

    Parameters:
    - tickers (list): List of stock tickers.
    - train_period (tuple): Tuple with start and end date for training (e.g., ("2024-01-01", "2024-06-30")).
    - test_period (tuple): Tuple with start and end date for testing (e.g., ("2024-07-01", "2024-12-31")).
    - max_weight (float): Maximum weight for any single asset (default is 20%).
    - risk_free_rate (float): Risk-free rate for Sharpe ratio calculation (default is 3%).

    Returns:
    - A dictionary with portfolio performance metrics and cumulative returns for testing.
    """

    # Fetch historical price data
    data = yf.download(tickers, start=train_period[0], end=test_period[1])['Adj Close']

    # Split into training and testing datasets
    train_data = data.loc[train_period[0]:train_period[1]]
    test_data = data.loc[test_period[0]:test_period[1]]

    # Calculate expected returns and covariance matrix on training data
    mu = expected_returns.mean_historical_return(train_data)
    S = risk_models.sample_cov(train_data)

    # Optimize Portfolio for Maximum Sharpe Ratio
    ef = EfficientFrontier(mu, S)
    ef.add_objective(objective_functions.L2_reg)  # Add regularization for stability
    ef.add_constraint(lambda w: w <= max_weight)  # Max weight constraint
    ef.add_constraint(lambda w: w >= 0.00)  # No short selling
    weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()

    # Print optimal weights
    print("\nOptimal Weights:")
    for stock, weight in cleaned_weights.items():
        print(f"{stock}: {weight:.2%}")

    # Backtest Portfolio on Test Data
    test_daily_returns = test_data.pct_change().dropna()
    weighted_daily_returns = test_daily_returns * pd.Series(cleaned_weights)
    test_portfolio_daily_returns = weighted_daily_returns.sum(axis=1)
    test_cumulative_returns = (1 + test_portfolio_daily_returns).cumprod()

    # Calculate test performance metrics
    test_annualized_return = test_portfolio_daily_returns.mean() * 252
    test_annualized_volatility = test_portfolio_daily_returns.std() * (252**0.5)
    test_sharpe_ratio = (test_annualized_return - risk_free_rate) / test_annualized_volatility

    # Print test performance metrics
    print("\nTest Data Performance:")
    print(f"Annualized Return: {test_annualized_return:.2%}")
    print(f"Annualized Volatility: {test_annualized_volatility:.2%}")
    print(f"Sharpe Ratio: {test_sharpe_ratio:.2f}")

    # Return performance metrics and cumulative returns
    return {
        "weights": cleaned_weights,
        "annualized_return": test_annualized_return,
        "annualized_volatility": test_annualized_volatility,
        "sharpe_ratio": test_sharpe_ratio,
        "cumulative_returns": test_cumulative_returns
    }

tickers = [
    'AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA', 'NVDA', 'MS',
    'GS', 'V', 'MA', 'KO', 'ADBE', 'JNJ', 'NEE', 'ENPH',
    'UNH', 'PFE', 'NKE'
]

train_period = ("2024-01-01", "2024-06-30")
test_period = ("2024-07-01", "2024-12-31")

results = portfolio_optimization(tickers, train_period, test_period)

# Plot cumulative returns
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
results["cumulative_returns"].plot(label="Optimized Portfolio (Test)", linewidth=2)
plt.title("Portfolio Performance on Test Data")
plt.xlabel("Date")
plt.ylabel("Cumulative Returns")
plt.legend()
plt.grid()
plt.show()
