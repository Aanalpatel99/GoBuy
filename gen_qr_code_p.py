import qrcode

# Define the product ID to be encoded in the QR code
product_id = "product123"

# Create a QR code
qr = qrcode.make(product_id)

# Save the QR code as an image
qr.save("product_qr_code.png")

print("QR code generated and saved as 'product_qr_code.png'")
