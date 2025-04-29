from flask import Flask, request, send_file, render_template, url_for
from datetime import datetime
import io
import sqlite3
from weasyprint import HTML
import os

app = Flask(__name__)

@app.route('/')
def form():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('index.html', current_date=current_date)

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    data = request.get_json()

    # Corrige formato de fecha si viene como dd/mm/yyyy
    try:
        if '/' in data.get('date', ''):
            date_obj = datetime.strptime(data['date'], "%d/%m/%Y")
            data['date'] = date_obj.strftime("%Y-%m-%d")
    except Exception as e:
        print("Error al parsear fecha:", e)
        data['date'] = datetime.now().strftime('%Y-%m-%d')

    invoice_number = save_to_db(data)

    # Generación del PDF
    try:
        print("Generando PDF...")
        rendered_html = render_template('invoice_template.html', data=data, invoice_number=invoice_number)
        pdf = HTML(string=rendered_html, base_url=os.path.abspath("static")).write_pdf()
        print("PDF generado correctamente")
    except Exception as e:
        print("Error al generar el PDF:", e)
        return "Error interno al generar el PDF", 500

    return send_file(
        io.BytesIO(pdf),
        as_attachment=True,
        download_name=f"Factura_{invoice_number}.pdf",
        mimetype='application/pdf'
    )

def save_to_db(data):
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, vehicle TEXT, address TEXT, vin TEXT,
            cityzip TEXT, lic TEXT, phone TEXT, mileage TEXT,
            color TEXT, description TEXT, total TEXT,
            invoice_number TEXT, created_at TEXT, date TEXT
        )
    ''')
    c.execute('SELECT COUNT(*) FROM invoices WHERE name = ?', (data.get('name',''),))
    count = c.fetchone()[0] + 1
    invoice_number = str(count).zfill(4)

    c.execute('''
        INSERT INTO invoices (name, vehicle, address, vin, cityzip, lic, phone,
        mileage, color, description, total, invoice_number, created_at, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name',''), data.get('vehicle',''), data.get('address',''), data.get('vin',''),
        data.get('cityzip',''), data.get('lic',''), data.get('phone',''), data.get('mileage',''),
        data.get('color',''), data.get('description',''), data.get('total',''),
        invoice_number, datetime.now().isoformat(), data.get('date','')
    ))
    conn.commit()
    conn.close()
    return invoice_number

if __name__ == "__main__":
    app.run(debug=True)
