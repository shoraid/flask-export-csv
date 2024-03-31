from flask import Flask, render_template, request, Response
import mysql.connector
import csv
import io

app = Flask(__name__)

# Setting MySQL
db_config = {
    'host': 'localhost', # host database
    'user': 'root', # username database
    'password': 'root', # password database
    'database': 'apollo_laravel_api' # nama database
}

@app.route('/')
def index():
    try:
        # Buat koneksi ke database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Ambil semua nama column
        cursor.execute("SHOW COLUMNS FROM users")
        columns = [column[0] for column in cursor.fetchall()]

        # Ambil tanggal mulai dan akhir dari html
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Pilih semua data
        query = "SELECT * FROM users"

        # Jika tanggal mulai dan akhir ada, maka eksekusi query Between
        if start_date and end_date:
            # Tambahkan query untuk mengambil data berdasarkan rentang waktu
            query = query + " WHERE created_at BETWEEN %s AND %s"

            # Tambahkan jam untuk memastikan data terambil sesuai tanggal
            start_date_with_time = start_date + ' 00:00:00'
            end_date_with_time = end_date + ' 23:59:59'

            # Gunakan method execute() untuk mengeksekusi query dengan tambahan parameter
            cursor.execute(query, (start_date_with_time, end_date_with_time))
        else:
            # Gunakan method execute() untuk mengeksekusi query
            cursor.execute(query)

        # Ambil data dari database
        rows = cursor.fetchall()

        # Ambil parameter download
        download = request.args.get('download')

        # Jika parameter download ada, eksekusi algoritma untuk export ke CSV
        if download:
            # Siapkan data CSV
            output = io.StringIO()
            writer = csv.writer(output) # Buat file CSV
            writer.writerow([i[0] for i in cursor.description])  # Buat header berdasarkan column di database
            writer.writerows(rows) # Masukkan data dari database ke CSV

            # Kembalikan response dengan data CSV yang sudah selesai di proses
            response = Response(output.getvalue(), mimetype='text/csv')
            response.headers["Content-Disposition"] = "attachment; filename=data.csv"

            return response

        # render halaman HTML
        return render_template('index.html', columns=columns, rows=rows, start_date=start_date, end_date=end_date)

    except mysql.connector.Error as err:
        return f"Error: {err}"

    finally:
        # Tutup koneksi ke database
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
