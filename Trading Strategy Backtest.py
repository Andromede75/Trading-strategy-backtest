# Trading Strategy Backtesting Project

# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# Function to ask user if they want to generate graphs
def ask_generate_graphs():
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    result = messagebox.askyesno("Generate Graphs", "Do you want to generate the graphs?")
    return result

# Download historical data for a chosen stock
stock_symbol = 'AAPL'
start_date = '2020-01-01'
end_date = '2023-01-01'
data = yf.download(stock_symbol, start=start_date, end=end_date)

# Compute daily returns
data['Daily Return'] = data['Adj Close'].pct_change()

# Define a simple moving average strategy (SMA)
short_window = 20  # Short-term moving average
long_window = 50   # Long-term moving average

# Calculate moving averages
data['SMA20'] = data['Adj Close'].rolling(window=short_window).mean()
data['SMA50'] = data['Adj Close'].rolling(window=long_window).mean()

# Define buy and sell signals
data['Signal'] = 0
data.loc[data['SMA20'] > data['SMA50'], 'Signal'] = 1  # Buy signal
data.loc[data['SMA20'] <= data['SMA50'], 'Signal'] = 0  # Sell signal

# Calculate strategy returns
data['Strategy Return'] = data['Signal'].shift(1) * data['Daily Return']

# Calculate performance metrics
sharpe_ratio = data['Strategy Return'].mean() / data['Strategy Return'].std() * np.sqrt(252)

def calculate_max_drawdown(returns):
    cumulative_returns = (1 + returns).cumprod()
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns / peak) - 1
    max_drawdown = drawdown.min()
    return max_drawdown

max_drawdown_strategy = calculate_max_drawdown(data['Strategy Return'])
max_drawdown_market = calculate_max_drawdown(data['Daily Return'])

# Sortino Ratio calculation
risk_free_rate = 0.01  # Assuming a risk-free rate of 1%
excess_return = data['Strategy Return'] - (risk_free_rate / 252)
downside_deviation = np.std(excess_return[excess_return < 0]) * np.sqrt(252)
sortino_ratio = excess_return.mean() / downside_deviation

# Add feature: Annualized returns and volatility
annualized_return = ((1 + data['Strategy Return'].mean()) ** 252) - 1
annualized_volatility = data['Strategy Return'].std() * np.sqrt(252)

# Display performance metrics in console
print(f'Sharpe Ratio: {sharpe_ratio:.2f}')
print(f'Sortino Ratio: {sortino_ratio:.2f}')
print(f'Max Drawdown (Strategy): {max_drawdown_strategy:.2%}')
print(f'Max Drawdown (Market): {max_drawdown_market:.2%}')
print(f'Annualized Return: {annualized_return:.2%}')
print(f'Annualized Volatility: {annualized_volatility:.2%}')

# Save the results to a CSV file
data.to_csv(f'{stock_symbol}_strategy_results.csv')

# Export key metrics to a text file
with open(f'{stock_symbol}_performance_metrics.txt', 'w') as f:
    f.write(f"Sharpe Ratio: {sharpe_ratio:.2f}\n")
    f.write(f"Sortino Ratio: {sortino_ratio:.2f}\n")
    f.write(f"Max Drawdown (Strategy): {max_drawdown_strategy:.2%}\n")
    f.write(f"Max Drawdown (Market): {max_drawdown_market:.2%}\n")
    f.write(f"Annualized Return: {annualized_return:.2%}\n")
    f.write(f"Annualized Volatility: {annualized_volatility:.2%}\n")

# Ask user if they want to generate graphs
if ask_generate_graphs():
    # Plot the strategy
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['Adj Close'], label='Price', alpha=0.5)
    plt.plot(data.index, data['SMA20'], label='SMA20', alpha=0.75)
    plt.plot(data.index, data['SMA50'], label='SMA50', alpha=0.75)
    plt.legend()
    plt.title(f'{stock_symbol} Price and Moving Averages')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.show()

    # Compute cumulative returns
    cumulative_strategy_return = (1 + data['Strategy Return']).cumprod()
    cumulative_market_return = (1 + data['Daily Return']).cumprod()

    # Plot cumulative returns
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, cumulative_strategy_return, label='Strategy Return')
    plt.plot(data.index, cumulative_market_return, label='Market Return')
    plt.legend()
    plt.title(f'Cumulative Returns: {stock_symbol}')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.show()

    # Additional visualization: Drawdown over time
    cumulative_returns_strategy = (1 + data['Strategy Return']).cumprod()
    peak_strategy = cumulative_returns_strategy.cummax()
    drawdown_strategy = (cumulative_returns_strategy / peak_strategy) - 1

    plt.figure(figsize=(14, 7))
    plt.plot(data.index, drawdown_strategy, label='Drawdown (Strategy)', color='red')
    plt.title(f'Drawdown Over Time: {stock_symbol}')
    plt.xlabel('Date')
    plt.ylabel('Drawdown')
    plt.legend()
    plt.show()
