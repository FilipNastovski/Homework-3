from flask import Flask, render_template, jsonify, request
import sqlite3
import subprocess
import pandas as pd

app = Flask(__name__)

DATABASE_PATH = "mse_stocks.db"


# Home page route
@app.route('/')
def home():
    return render_template('index.html')


# Route to run main.py (filling issuer_codes table)
@app.route('/scrape_data', methods=['POST'])
def scrape_data():
    try:
        subprocess.run(["python", "main.py"], check=True)
        return jsonify({"message": "Data scraped successfully."}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"message": f"Error running main script: {str(e)}"}), 500


# Route to run TechnicalAnalysis.py
@app.route('/run_analysis', methods=['POST'])
def run_analysis():
    try:
        subprocess.run(["python", "TechnicalAnalysis.py"], check=True)
        return jsonify({"message": "Technical analysis completed successfully."}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"message": f"Error running technical analysis script: {str(e)}"}), 500


# Route to fetch issuer codes (for dropdown)
@app.route('/get_issuer_codes', methods=['GET'])
def get_issuer_codes():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        query = "SELECT DISTINCT issuer_code FROM stock_data"
        issuer_codes = pd.read_sql_query(query, conn)['issuer_code'].tolist()
        conn.close()
        return jsonify(issuer_codes), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching issuer codes: {str(e)}"}), 500


@app.route('/fetch_latest_analysis', methods=['GET'])
def fetch_latest_analysis():
    try:
        issuer_code = request.args.get('issuer_code')
        time_period = request.args.get('time_period')

        # Determine the appropriate SQL query based on the time period
        if time_period == "daily":
            query = f"SELECT * FROM technical_indicators WHERE issuer_code = ? AND time_period = 'daily' ORDER BY Date DESC LIMIT 1"
        elif time_period == "weekly":
            query = f"SELECT * FROM technical_indicators WHERE issuer_code = ? AND time_period = 'weekly' ORDER BY Date DESC LIMIT 1"
        elif time_period == "monthly":
            query = f"SELECT * FROM technical_indicators WHERE issuer_code = ? AND time_period = 'monthly' ORDER BY Date DESC LIMIT 1"
        else:
            return jsonify({"message": "Invalid time period selected."}), 400

        conn = sqlite3.connect(DATABASE_PATH)
        df = pd.read_sql_query(query, conn, params=(issuer_code,))
        conn.close()

        if df.empty:
            return jsonify({"message": "No data available for the selected issuer and time period."}), 404

        # Replace NaN/NULL with "No Data"
        df = df.fillna("No Data")

        # Return the latest analysis data
        return jsonify(df.to_dict(orient='records')), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching latest analysis data: {str(e)}"}), 500


@app.route('/fetch_historical_analysis', methods=['GET'])
def fetch_historical_analysis():
    try:
        issuer_code = request.args.get('issuer_code')
        time_period = request.args.get('time_period')

        # Build the query based on time period (Daily, Weekly, Monthly)
        if time_period == "daily":
            query = f"SELECT * FROM technical_indicators WHERE issuer_code = ? AND time_period = 'daily'"
        elif time_period == "weekly":
            query = f"SELECT * FROM technical_indicators WHERE issuer_code = ? AND time_period = 'weekly'"
        elif time_period == "monthly":
            query = f"SELECT * FROM technical_indicators WHERE issuer_code = ? AND time_period = 'monthly'"
        else:
            return jsonify({"message": "Invalid time period selected."}), 400

        query += " ORDER BY Date DESC LIMIT 100"

        conn = sqlite3.connect(DATABASE_PATH)
        df = pd.read_sql_query(query, conn, params=(issuer_code,))
        conn.close()

        if df.empty:
            return jsonify({"message": "No data available for the selected time period."}), 404

        # Replace NaN/NULL with "No Data"
        df = df.fillna("No Data")

        # Return the historical data
        return jsonify(df.to_dict(orient='records')), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching historical analysis data: {str(e)}"}), 500



if __name__ == "__main__":
    app.run(debug=True)
