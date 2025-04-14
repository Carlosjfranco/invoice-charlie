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
    form.reset();
  } else {
    alert("Error generando la factura");
  }
});
