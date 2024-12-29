# Stock Market Analysis Web Application

## Project Overview

This project is a web-based application designed to automate stock market analysis for the Macedonian Stock Exchange (MSE). The application scrapes historical stock data, performs technical analysis, and provides sentiment analysis using NLP. The final goal is to provide users with a clear view of market trends and make stock trading decisions based on the analysis.

## Features

1. **Stock Data Scraping**: 
   - The app scrapes stock data from an external source, populating an internal SQLite database.
   - The `main.py` script performs the data scraping and stores the data in the `stock_data` table.

2. **Technical Analysis**:
   - The `TechnicalAnalysis.py` script processes the stock data to generate technical indicators such as moving averages, relative strength index (RSI), and more.
   - The analysis results are stored in the `technical_indicators` table in the database.

3. **Frontend Interface**:
   - The web interface allows users to:
     - Select an issuer code (stock symbol) from a dropdown.
     - Choose an analysis time period (daily, weekly, or monthly).
     - Run data scraping and technical analysis with the click of a button.
     - Display the latest technical analysis for the selected stock and time period.
     - View historical analysis data and display buy, sell, or hold signals.

4. **Signals**:
   - The system calculates and displays signals (Buy, Sell, Hold) based on the technical analysis.
   - These signals are displayed with corresponding color codes (green for Buy, red for Sell, orange for Hold).

## Technologies Used

- **Backend**: Flask, Python
  - `Flask` is used to serve the web application.
  - `SQLite` is used for data storage.
  - `Pandas` for data manipulation.
  - `Selenium`, `requests`, and `BeautifulSoup` for web scraping.
  - `subprocess` to execute Python scripts for scraping and analysis.

- **Frontend**: HTML, CSS, JavaScript (jQuery)
  - Dark theme user interface.
  - Buttons for triggering scripts (scraping and analysis).
  - Dropdowns for selecting issuer code and time period.
  - Tables to display stock analysis data and signals.

## Video Recording

A video recording demonstrating the functionalities of the Stock Market Analysis Web Application can be found in the `Media` folder. The video showcases how the application scrapes data, performs technical analysis, and displays stock signals.

## How It Works

1. **Data Scraping**:
   - The `Scrape data` button triggers the `main.py` script, which scrapes stock data and stores it in the `stock_data` table in the SQLite database.
   
2. **Technical Analysis**:
   - The `Run analysis` button triggers the `TechnicalAnalysis.py` script, which analyzes the stock data and calculates technical indicators. The results are stored in the `technical_indicators` table.
   
3. **Displaying Analysis**:
   - Users can select a stock symbol and a time period (daily, weekly, or monthly) from the frontend interface.
   - The application fetches the latest analysis for the selected stock and displays it in a table.
   - The `Buy`, `Sell`, or `Hold` signals are displayed below the table with corresponding colors.
   
4. **Data Fetching**:
   - The backend routes fetch data from the database and return it in JSON format to be displayed in the frontend tables.

5. **Database**:
   - SQLite is used as the database to store scraped stock data and technical analysis results.
