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
    data['SMA_20'] = data['Last Trade Price'].rolling(window=20).mean()  # Simple Moving Average
    data['SMA_50'] = data['Last Trade Price'].rolling(window=50).mean()
    data['EMA_20'] = data['Last Trade Price'].ewm(span=20).mean()  # Exponential Moving Average
    data['EMA_50'] = data['Last Trade Price'].ewm(span=50).mean()

    # Oscillators
    data['RSI'] = ta.momentum.RSIIndicator(close=data['Last Trade Price']).rsi()  # Relative Strength Index
    data['MACD'] = ta.trend.MACD(close=data['Last Trade Price']).macd()  # MACD
    data['Stoch'] = ta.momentum.StochasticOscillator(
        high=data['Max'], low=data['Min'], close=data['Last Trade Price']
    ).stoch()
    data['CCI'] = ta.trend.CCIIndicator(
        high=data['Max'], low=data['Min'], close=data['Last Trade Price']
    ).cci()
    # Replace Momentum with Williams %R as ta library doesn't have MomentumIndicator
    data['Williams %R'] = ta.momentum.WilliamsRIndicator(
        high=data['Max'], low=data['Min'], close=data['Last Trade Price']
    ).williams_r()

    # Generate buy/sell/hold signals based on indicators
    data['Signal'] = 'Hold'
    data.loc[data['RSI'] < 30, 'Signal'] = 'Buy'  # RSI Oversold
    data.loc[data['RSI'] > 70, 'Signal'] = 'Sell'  # RSI Overbought
    data.loc[data['Last Trade Price'] > data['SMA_20'], 'Signal'] = 'Buy'  # Price above SMA_20
    data.loc[data['Last Trade Price'] < data['SMA_20'], 'Signal'] = 'Sell'  # Price below SMA_20

    return data


# Function to resample and calculate indicators
def analyze_for_time_period(data, period):
    """
    Resamples the data for the given time period and calculates indicators.
    Returns the analyzed data with the time period added.
    """
    if period == 'daily':
        resampled_data = data  # No resampling needed for daily
    elif period == 'weekly':
        resampled_data = data.set_index('Date').resample('W').agg({
            'Last Trade Price': 'mean',
            'Max': 'max',
            'Min': 'min',
            'Volume': 'sum'
        }).reset_index()
    elif period == 'monthly':
        resampled_data = data.set_index('Date').resample('ME').agg({
            'Last Trade Price': 'mean',
            'Max': 'max',
            'Min': 'min',
            'Volume': 'sum'
        }).reset_index()
    else:
        raise ValueError("Invalid period. Must be 'daily', 'weekly', or 'monthly'.")

    analyzed_data = calculate_indicators(resampled_data)
    analyzed_data['time_period'] = period
    return analyzed_data


# Technical analysis function
def technical_analysis(database_path):
    """
    Performs technical analysis on stock data stored in the SQLite database.
    Calculates indicators for three time periods: daily, weekly, and monthly.
    Saves the results in a single table called 'technical_indicators'.
    """
    # Connect to SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Fetch stock data
    query = '''
    SELECT 
        issuer_code, 
        "Date", 
        "Last Trade Price", 
        "Max", 
        "Min", 
        "Volume", 
        "Turnover in BEST (denars)" 
    FROM stock_data
    '''
    stock_data = pd.read_sql_query(query, conn)

    # Ensure data types are correct
    stock_data['Date'] = pd.to_datetime(stock_data['Date'])
    stock_data = stock_data.sort_values(by=['issuer_code', 'Date'])

    # Perform analysis for each issuer_code and time period
    periods = ['daily', 'weekly', 'monthly']
    results = []
    for issuer in stock_data['issuer_code'].unique():
        issuer_data = stock_data[stock_data['issuer_code'] == issuer].copy()  # Avoid SettingWithCopyWarning
        for period in periods:
            analyzed_data = analyze_for_time_period(issuer_data, period)
            analyzed_data['issuer_code'] = issuer
            results.append(analyzed_data)

    # Combine all results into a single DataFrame
    results_df = pd.concat(results, ignore_index=True)

    # Save the results into the database
    results_df[['issuer_code', 'Date', 'time_period', 'Signal', 'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50',
                'RSI', 'MACD', 'Stoch', 'CCI', 'Williams %R']].to_sql(
        'technical_indicators', conn, if_exists='replace', index=False
    )

    # Close the database connection
    conn.close()
    print("Technical analysis completed and saved to 'technical_indicators' table.")


# Run technical analysis
if __name__ == "__main__":
    DATABASE_PATH = "mse_stocks.db"
    technical_analysis(DATABASE_PATH)
