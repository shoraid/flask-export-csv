from flask import Flask, render_template, request, Response
import mysql.connector
import csv
import io

app = Flask(__name__)

# MySQL database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'apollo_laravel_api'
}

@app.route('/')
def index():
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Fetch column names
        cursor.execute("SHOW COLUMNS FROM users")
        columns = [column[0] for column in cursor.fetchall()]

        # Fetch data from the database
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()

        return render_template('index.html', columns=columns, rows=rows)

    except mysql.connector.Error as err:
        return f"Error: {err}"

    finally:
        # Close database connections
        if 'conn' in locals():
            conn.close()

@app.route('/download_csv', methods=['POST'])
def download_csv():
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Fetch data from the database
        query = "SELECT * FROM users"
        cursor.execute(query)
        data = cursor.fetchall()

        # Prepare CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([i[0] for i in cursor.description])  # Write column headers
        writer.writerows(data)

        # Create a Flask response with CSV data
        response = Response(output.getvalue(), mimetype='text/csv')
        response.headers["Content-Disposition"] = "attachment; filename=data.csv"

        return response

    except mysql.connector.Error as err:
        return f"Error: {err}"

    finally:
        # Close database connections
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
