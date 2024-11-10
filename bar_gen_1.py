import barcode
from barcode.writer import ImageWriter

# Product data to encode in barcodes
product_data = {
    "product123": {"name": "Product A", "price": 15.0},
    "product456": {"name": "Product B", "price": 20.0},
    "product789": {"name": "Product C", "price": 25.0}
}

# Generate barcodes for products
for product_id, info in product_data.items():
    ean = barcode.get('code128', product_id, writer=ImageWriter())
    filename = ean.save(f"{product_id}")
    print(f"Barcode generated for {info['name']} and saved as {filename}.png")
