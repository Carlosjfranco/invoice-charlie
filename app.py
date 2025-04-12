
from flask import Flask, request, send_file, render_template
from reportlab.pdfgen import canvas
import io
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('index.html')

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    data = request.json
    save_to_db(data)
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 800, f"Cliente: {data['name']}")
    c.drawString(100, 780, f"Vehículo: {data['vehicle']}")
    c.drawString(100, 760, f"Dirección: {data['address']}")
    c.drawString(100, 740, f"VIN: {data['vin']}")
    c.drawString(100, 720, f"Ciudad/ZIP: {data['cityzip']}")
    c.drawString(100, 700, f"Placa: {data['lic']}")
    c.drawString(100, 680, f"Teléfono: {data['phone']}")
    c.drawString(100, 660, f"Millaje: {data['mileage']}")
    c.drawString(100, 640, f"Color: {data['color']}")
    c.drawString(100, 620, f"Descripción del trabajo:")
    text_object = c.beginText(100, 600)
    for line in data['description'].splitlines():
        text_object.textLine(line)
    c.drawText(text_object)
    c.drawString(100, text_object.getY() - 20, f"Total: ${data['total']}")
    c.drawString(100, 600, f"Fecha: {data.get('date', datetime.now().strftime('%Y-%m-%d'))}")
    c.showPage()
    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="invoice.pdf", mimetype='application/pdf')

def save_to_db(data):
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, vehicle TEXT, address TEXT, vin TEXT,
            cityzip TEXT, lic TEXT, phone TEXT, mileage TEXT,
            color TEXT, description TEXT, total TEXT, created_at TEXT, date TEXT
        )
    ''')
    c.execute('''
        INSERT INTO invoices (name, vehicle, address, vin, cityzip, lic, phone, mileage, color, total, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'], data['vehicle'], data['address'], data['vin'],
        data['cityzip'], data['lic'], data['phone'], data['mileage'],
        data['color'], data['description'], data['total'], data.get('date', datetime.now().isoformat())
    ))
    conn.commit()
    conn.close()


import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

