from flask import Flask, request, send_file, render_template
from reportlab.pdfgen import canvas
import io
from datetime import datetime
import os

# Se especifica la carpeta de plantillas explícitamente, aunque es el valor por defecto
app = Flask(__name__, template_folder="templates")

@app.route('/')
def form():
    return render_template('index.html')

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    data = request.json
    print("Datos recibidos:", data)  # Esto simula la persistencia (en lugar de guardar en base de datos)

    # Crear un buffer en memoria para el PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    # Generar el contenido del PDF
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

# IMPORTANTE: No se debe incluir ningún bloque de arranque (if __name__ == '__main__')
