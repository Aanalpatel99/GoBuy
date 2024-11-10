from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivy.clock import Clock
import cv2
from pyzbar.pyzbar import decode
from reportlab.pdfgen import canvas
import os
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color

# Wallet class for customer balances
class Wallet:
    def __init__(self, initial_balance=100.0):
        """Initializes the wallet with a starting balance."""
        self.balance = initial_balance

    def get_balance(self):
        """Returns the current balance."""
        return self.balance

    def deduct_amount(self, amount):
        """Deducts the specified amount from the wallet if sufficient funds are available."""
        if self.balance >= amount:
            self.balance -= amount
            return True
        else:
            return False

# Class for displaying the camera feed and scanning QR codes
class CameraPreview(Image):
    def __init__(self, capture, fps=30, **kwargs):
        """Initializes the camera preview widget."""
        super().__init__(**kwargs)
        self.capture = capture
        self.fps = fps
        Clock.schedule_interval(self.update, 1.0 / self.fps)

    def update(self, dt):
        """Updates the camera feed and scans for QR codes."""
        if not self.capture.isOpened():
            print("Error: Camera is not opened.")
            return
        
        ret, frame = self.capture.read()
        if not ret:
            print("Error: Failed to read from the camera.")
            return
        
        try:
            # Rotate the frame 180 degrees to correct the upside-down view
            frame = cv2.rotate(frame, cv2.ROTATE_180)

            buf = frame.tobytes()

            if not self.texture or self.texture.size != (frame.shape[1], frame.shape[0]):
                from kivy.graphics.texture import Texture
                self.texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                self.texture.flip_vertical()
            self.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.canvas.ask_update()

            # Scan for QR codes
            decoded_objects = decode(frame)
            for obj in decoded_objects:
                print(f"QR Code detected: {obj.data.decode('utf-8')}")
                self.parent.process_qr_data(obj.data.decode('utf-8'))
                break
        except Exception as e:
            print(f"An error occurred during frame update: {e}")

# Screen class for QR code scanning, payment processing, and receipt generation
class QRCodeScannerScreen(Screen):
    def __init__(self, app, wallet, **kwargs):
        """Initializes the QR code scanner screen."""
        super().__init__(**kwargs)
        self.app = app
        self.wallet = wallet
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("Error: Unable to access the camera.")
            return
        print("Camera successfully opened.")
        
        # Main layout for the screen
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Header layout for wallet and buttons
        header_layout = GridLayout(cols=3, size_hint_y=None, height='60dp')
        
        # Wallet balance label with brackets
        with self.canvas.before:
            Color(1, 1, 1, 1)  # White color for the background of the label
            self.rect = Rectangle(pos=(20, self.height - 70), size=(self.width - 40, 40))
        
        self.balance_label = MDLabel(
            text=f"[Wallet Balance: ${self.wallet.get_balance():.2f}]",
            halign="center",
            theme_text_color="Secondary",
            markup=True,
            font_style="H6"
        )
        header_layout.add_widget(self.balance_label)
        
        # Add "Coupons" and "Points" buttons
        self.coupons_button = MDRaisedButton(
            text="Coupons",
            pos_hint={"center_x": 0.5}
        )
        self.points_button = MDRaisedButton(
            text="Points",
            pos_hint={"center_x": 0.5}
        )
        header_layout.add_widget(self.coupons_button)
        header_layout.add_widget(self.points_button)

        main_layout.add_widget(header_layout)
        
        # Empty box for advertisements
        ad_box = Widget(size_hint_y=None, height='60dp')
        ad_box_canvas = ad_box.canvas
        with ad_box_canvas:
            Color(0.9, 0.9, 0.9, 1)  # Light gray for the advertisement box
            Rectangle(pos=ad_box.pos, size=ad_box.size)
        main_layout.add_widget(ad_box)

        # Add the camera preview
        self.camera_preview = CameraPreview(capture=self.capture)
        main_layout.add_widget(self.camera_preview)

        # Add a button for generating the receipt
        self.receipt_button = MDRaisedButton(
            text="Generate Receipt",
            pos_hint={"center_x": 0.5},
            size_hint=(0.3, 0.1),
            on_release=lambda x: self.app.generate_receipt()
        )
        main_layout.add_widget(self.receipt_button)
        
        # Add the layout to the screen
        self.add_widget(main_layout)

    def process_qr_data(self, data):
        """Processes the QR code data, identifies the product, and deducts the price from the wallet."""
        # Simulated product database (replace with real database or API call)
        product_database = {
            "product123": {"name": "Product A", "price": 15.0},
            "product456": {"name": "Product B", "price": 20.0},
            "product789": {"name": "Product C", "price": 25.0}
        }

        # Extract product information from the QR code data
        product_id = data  # Assume the QR code contains the product ID
        product_info = product_database.get(product_id)

        if product_info:
            item_name = product_info["name"]
            item_price = product_info["price"]
            
            if self.wallet.deduct_amount(item_price):
                print(f"Scanned item: {item_name}, Price: ${item_price:.2f}")
                try:
                    # Log the transaction to a file for receipt generation
                    with open("transactions.txt", "a") as file:
                        file.write(f"Scanned item: {item_name}, Price: ${item_price:.2f}\n")
                    print(f"Payment of ${item_price:.2f} processed for: {item_name}")
                    
                    # Update the balance display
                    self.balance_label.text = f"[Wallet Balance: ${self.wallet.get_balance():.2f}]"
                except Exception as e:
                    print(f"Error writing to file: {e}")
            else:
                print("Insufficient balance. Payment failed.")
        else:
            print("Product not found in the database. Payment not processed.")

    def on_leave(self):
        """Releases the camera when leaving the screen."""
        if self.capture.isOpened():
            self.capture.release()
            print("Camera released.")

# Main app class for managing the app and generating receipts
class MainApp(MDApp):
    def build(self):
        """Builds the main app and initializes the wallet."""
        self.wallet = Wallet(initial_balance=100.0)  # Set an initial balance for testing
        sm = ScreenManager()
        screen = QRCodeScannerScreen(app=self, wallet=self.wallet, name='scanner')
        sm.add_widget(screen)
        return sm

    def generate_receipt(self):
        """Generates a PDF receipt from the transactions file."""
        if os.path.exists("transactions.txt"):
            try:
                c = canvas.Canvas("receipt.pdf")
                c.drawString(100, 800, "Transaction Receipt")
                with open("transactions.txt", "r") as file:
                    lines = file.readlines()
                    y = 780
                    for line in lines:
                        c.drawString(100, y, line.strip())
                        y -= 20
                c.save()
                print("Receipt generated as receipt.pdf")
            except Exception as e:
                print(f"Error generating receipt: {e}")
        else:
            print("No transactions to include in the receipt.")

# Run the app
if __name__ == '__main__':
    try:
        MainApp().run()
    except Exception as e:
        print(f"App crashed: {e}")
