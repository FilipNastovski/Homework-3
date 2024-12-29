from flask import Flask, render_template, request, jsonify
import subprocess
import sqlite3
import pandas as pd

app = Flask(__name__)

DATABASE_PATH = "mse_stocks.db"


# Home page route
@app.route('/')
def home():
    return render_template('index.html')


# Route to run main.py (filling issuer_codes table)
@app.route('/run_main', methods=['POST'])
def run_main():
    try:
        subprocess.run(["python", "main.py"], check=True)
        return jsonify({"message": "Main script executed successfully."}), 200
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


# Route to fetch data from the database
@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        query = "SELECT * FROM technical_indicators"
        df = pd.read_sql_query(query, conn)
        conn.close()
        data = df.to_dict(orient='records')
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching data: {str(e)}"}), 500


# Route to fetch analysis data from the 'technical_indicators' table
@app.route('/get_issuer_codes', methods=['GET'])
def get_issuer_codes():
    try:
        print("Fetching issuer codes from the stock_data table...")  # Log message to confirm the route is being hit

        # Connect to SQLite and fetch distinct issuer codes from 'stock_data' table
        conn = sqlite3.connect(DATABASE_PATH)
        query = "SELECT DISTINCT issuer_code FROM stock_data"
        df = pd.read_sql_query(query, conn)
        conn.close()

        print("Issuer codes fetched successfully.")  # Log success message

        # Convert DataFrame to list of issuer codes
        issuer_codes = df['issuer_code'].tolist()

        # Return the issuer codes as JSON
        return jsonify(issuer_codes), 200
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Log the error
        return jsonify({"message": f"Error fetching issuer codes: {str(e)}"}), 500


@app.route('/fetch_filtered_analysis_data', methods=['GET'])
def fetch_filtered_analysis_data():
    try:
        issuer_code = request.args.get('issuer_code')
        time_period = request.args.get('time_period')

        print(f"Fetching data for issuer: {issuer_code} and time period: {time_period}...")

        # Connect to SQLite and fetch filtered data based on issuer_code and time_period
        conn = sqlite3.connect(DATABASE_PATH)
        query = f"SELECT * FROM technical_indicators WHERE issuer_code = ? AND time_period = ?"
        df = pd.read_sql_query(query, conn, params=(issuer_code, time_period))
        conn.close()

        print("Filtered data fetched successfully.")

        # Replace NaN or NULL values with a placeholder (e.g., "N/A")
        df = df.fillna("N/A")

        # Convert DataFrame to dictionary for JSON response
        data = df.to_dict(orient='records')

        # Return the data as JSON
        return jsonify(data), 200
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Log the error
        return jsonify({"message": f"Error fetching filtered data: {str(e)}"}), 500



if __name__ == "__main__":
    app.run(debug=True)
