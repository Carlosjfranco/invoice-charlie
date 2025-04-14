from flask import Flask, request, send_file, render_template
from reportlab.pdfgen import canvas
import io
import sqlite3
from datetime import datetime
import os

app = Flask(__name__, template_folder="templates")

@app.route('/')
def form():
    return render_template('index.html')

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    data = request.json
    print("Datos recibidos:", data)  # Para verificar en los logs
    
    # Guarda la info en la base de datos y obtiene el número correlativo para el cliente
    invoice_number = save_to_db(data)
    
    # Crea el PDF en memoria
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    
    # Agrega el número de factura (correlativo)
    c.drawString(100, 820, f"N° Factura: {invoice_number}")
    c.drawString(100, 800, f"Cliente: {data.get('name', '')}")
    c.drawString(100, 780, f"Vehículo: {data.get('vehicle', '')}")
    c.drawString(100, 760, f"Dirección: {data.get('address', '')}")
    c.drawString(100, 740, f"VIN: {data.get('vin', '')}")
    c.drawString(100, 720, f"Ciudad/ZIP: {data.get('cityzip', '')}")
    c.drawString(100, 700, f"Placa: {data.get('lic', '')}")
    c.drawString(100, 680, f"Teléfono: {data.get('phone', '')}")
    c.drawString(100, 660, f"Millaje: {data.get('mileage', '')}")
    c.drawString(100, 640, f"Color: {data.get('color', '')}")
    c.drawString(100, 620, "Descripción del trabajo:")
    
    text_object = c.beginText(100, 600)
    for line in data.get('description', '').splitlines():
        text_object.textLine(line)
    c.drawText(text_object)
    
    c.drawString(100, text_object.getY() - 20, f"Total: ${data.get('total', '')}")
    c.drawString(100, text_object.getY() - 40, f"Fecha: {data.get('date', datetime.now().strftime('%Y-%m-%d'))}")
    
    c.showPage()
    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="invoice.pdf", mimetype='application/pdf')

def save_to_db(data):
    # Conecta a la base de datos (se crea el archivo invoices.db en el servidor)
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    # Crea la tabla si aún no existe (incluye la columna invoice_number)
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            vehicle TEXT,
            address TEXT,
            vin TEXT,
            cityzip TEXT,
            lic TEXT,
            phone TEXT,
            mileage TEXT,
            color TEXT,
            description TEXT,
            total TEXT,
            invoice_number TEXT,
            created_at TEXT,
            date TEXT
        )
    ''')
    # Obtén la cuenta de facturas ya registradas para este cliente (según el nombre)
    c.execute('SELECT COUNT(*) FROM invoices WHERE name = ?', (data.get('name', ''),))
    count = c.fetchone()[0]
    invoice_num_int = count + 1
    invoice_number = str(invoice_num_int).zfill(4)  # Formatea a 4 dígitos, ej.: 0001, 0002, etc.
    
    # Inserta la nueva factura en la base de datos, incluyendo el número de factura
    c.execute('''
        INSERT INTO invoices 
        (name, vehicle, address, vin, cityzip, lic, phone, mileage, color, description, total, invoice_number, created_at, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name', ''),
        data.get('vehicle', ''),
        data.get('address', ''),
        data.get('vin', ''),
        data.get('cityzip', ''),
        data.get('lic', ''),
        data.get('phone', ''),
        data.get('mileage', ''),
        data.get('color', ''),
        data.get('description', ''),
        data.get('total', ''),
        invoice_number,
        datetime.now().isoformat(),
        data.get('date', datetime.now().strftime('%Y-%m-%d'))
    ))
    conn.commit()
    conn.close()
    return invoice_number
