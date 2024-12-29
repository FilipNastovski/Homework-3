import pandas as pd
import sqlite3
import ta


# Define technical indicators
def calculate_indicators(data):
    """
    Calculates technical indicators for the given data.
    Returns the data with indicators and signals.
    """
    # Moving Averages (MA)
    data['SMA_20'] = data['last_trade_price'].rolling(window=20).mean()  # Simple Moving Average
    data['SMA_50'] = data['last_trade_price'].rolling(window=50).mean()
    data['EMA_20'] = data['last_trade_price'].ewm(span=20).mean()  # Exponential Moving Average
    data['EMA_50'] = data['last_trade_price'].ewm(span=50).mean()

    # Oscillators
    data['RSI'] = ta.momentum.RSIIndicator(data['last_trade_price']).rsi()  # Relative Strength Index
    data['MACD'] = ta.trend.MACD(data['last_trade_price']).macd()  # MACD
    data['Stoch'] = ta.momentum.StochasticOscillator(data['high'], data['low'], data['last_trade_price']).stoch()
    data['CCI'] = ta.trend.CCIIndicator(data['high'], data['low'], data['last_trade_price']).cci()
    data['Momentum'] = ta.momentum.MomentumIndicator(data['last_trade_price']).momentum()

    # Generate buy/sell/hold signals based on indicators
    data['Signal'] = 'Hold'
    data.loc[data['RSI'] < 30, 'Signal'] = 'Buy'  # RSI Oversold
    data.loc[data['RSI'] > 70, 'Signal'] = 'Sell'  # RSI Overbought
    data.loc[data['last_trade_price'] > data['SMA_20'], 'Signal'] = 'Buy'  # Price above SMA_20
    data.loc[data['last_trade_price'] < data['SMA_20'], 'Signal'] = 'Sell'  # Price below SMA_20

    return data


# Technical analysis function
def technical_analysis(database_path):
    """
    Performs technical analysis on stock data stored in the SQLite database.
    Saves the results in a new table called 'technical_indicators'.
    """
    # Connect to SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Fetch stock data
    query = "SELECT issuer_code, date, last_trade_price, max, min, volume, turnover FROM stock_data"
    stock_data = pd.read_sql_query(query, conn)

    # Ensure data types are correct
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    stock_data = stock_data.sort_values(by=['issuer_code', 'date'])

    # Perform analysis for each issuer_code
    results = []
    for issuer in stock_data['issuer_code'].unique():
        issuer_data = stock_data[stock_data['issuer_code'] == issuer]
        analyzed_data = calculate_indicators(issuer_data)

        # Add the issuer_code back and append results
        analyzed_data['issuer_code'] = issuer
        results.append(analyzed_data)

    # Combine all results into a single DataFrame
    results_df = pd.concat(results, ignore_index=True)

    # Save the results into the database
    results_df[['issuer_code', 'date', 'Signal', 'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50',
                'RSI', 'MACD', 'Stoch', 'CCI', 'Momentum']].to_sql(
        'technical_indicators', conn, if_exists='replace', index=False
    )

    # Close the database connection
    conn.close()
    print("Technical analysis completed and saved to 'technical_indicators' table.")


# Run technical analysis
if __name__ == "__main__":
    DATABASE_PATH = "path/to/your/stock_data.db"
    technical_analysis(DATABASE_PATH)
