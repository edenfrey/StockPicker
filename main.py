import datetime
import yfinance as yf
import pandas as pd
import numpy as np

# List of stocks to analyze
stock_list = []

def calculate_score(df):
    # Calculate the average return
    avg_return = (df['Close'][-1] - df['Close'][0]) / df['Close'][0]
    
    # Calculate the standard deviation of returns
    std_return = df['Close'].pct_change().std()
    
    # Calculate the Sharpe ratio
    sharpe_ratio = avg_return / std_return
    
    # Calculate the RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.iloc[-1]
    
    # Calculate the MACD
    short_ema = df['Close'].ewm(span=12, adjust=False).mean()
    long_ema = df['Close'].ewm(span=26, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal
    macd = histogram.iloc[-1]
    
    # Calculate the Bollinger Bands
    rolling_mean = df['Close'].rolling(window=20).mean()
    rolling_std = df['Close'].rolling(window=20).std()
    upper_band = rolling_mean + 2 * rolling_std
    lower_band = rolling_mean - 2 * rolling_std
    bollinger = (df['Close'][-1] - lower_band[-1]) / (upper_band[-1] - lower_band[-1])
    
    # Assign weights to each calculation
    avg_return_weight = 0.3
    sharpe_ratio_weight = 0.3
    rsi_weight = 0.1
    macd_weight = 0.1
    bollinger_weight = 0.2
    
    # Calculate the overall score
    score = avg_return_weight * avg_return + sharpe_ratio_weight * sharpe_ratio + rsi_weight * rsi + macd_weight * macd + bollinger_weight * bollinger
    
    return score


# Dictionary to store the stock and its associated score
stock_scores = {}

# Current date
now = datetime.datetime.now()

# Loop through each stock in the list and calculate its score
# Open the text file for reading
with open("listofstocks.txt", "r") as stock_list:
	# Loop through each line in the file
	for stock in stock_list:
		try:
			stock = stock.strip()
			# Download the historical data for the past 1 year
			end_date = now.strftime("%Y-%m-%d")
			start_date = (now - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
			df = yf.download(stock, start=start_date, end=end_date)

			# Calculate the overall score for the stock
			score = calculate_score(df)

			# Check if the score is not NAN
			if not np.isnan(score):
				# Add the stock and its score to the dictionary
				stock_scores[stock] = score

		except Exception as e:
			continue

	# Rank the stocks based on the scores
	ranked_stocks = sorted(stock_scores.items(), key=lambda x: x[1], reverse=True)


# Budget
N = 117.99 # Example budget of $5000
# Keep track of the remaining budget
remaining_budget = N

# Keep track of the stocks and their amount
purchased_stocks = {}

# Loop through each ranked stock and buy as many shares as possible
count = 0
for stock, score in ranked_stocks:
	count += 1
	if remaining_budget == 0 or count > 50:
		break
	else:
		try:
			# Get the latest stock price
			stock_info = yf.Ticker(stock).history(period="1d")
			latest_price = stock_info['Close'].iloc[-1]
			cost = 100 * latest_price
			count2 = 0

			while remaining_budget >= cost + 7 and count2 < 2 and cost > 50:
				count2 += 1
				remaining_budget -= cost		 
				purchased_stocks[stock] = count2
			if count2 > 0:
				remaining_budget -= 7
				
		except Exception as e:
			continue

# Output the stocks and their shares purchased
print("Top stocks to buy based on budget:")
for stock, cost in purchased_stocks.items():
    print(f"Stock: {stock} | Amount: {cost}")