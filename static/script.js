document.getElementById("invoiceForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const form = e.target;
  const formData = new FormData(form);
  const data = {};
  formData.forEach((val, key) => data[key] = val);
  
  const response = await fetch("/generate_invoice", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  
  if (response.ok) {
    const blob = await response.blob();
    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = "invoice.pdf";
    link.click();
    // Limpia el formulario y reestablece el campo fecha
    form.reset();
    // Para asegurar el valor de fecha: usamos el valor por defecto
    document.getElementById("dateField").value = new Date().toISOString().slice(0, 10);
  } else {
    alert("Error generando la factura");
  }
});

const descField = document.getElementById("description");
descField.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    const lines = descField.value.split('\n').length;
    if (lines >= 5) {
      e.preventDefault();
    }
  }
});