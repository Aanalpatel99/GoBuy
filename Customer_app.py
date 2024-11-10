from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import cv2
from pyzbar.pyzbar import decode
import os
from kivy.uix.image import Image

# Wallet class for customer balances
class Wallet:
    def __init__(self, initial_balance=100.0):
        """Initializes the wallet with a starting balance."""
        self.balance = initial_balance

    def get_balance(self):
        """Returns the current balance."""
        return self.balance

# Screen class for the main UI with wallet balance and buttons
class MainScreen(Screen):
    def __init__(self, app, wallet, **kwargs):
        """Initializes the main screen with wallet, advertisement box, and buttons."""
        super().__init__(**kwargs)
        self.app = app
        self.wallet = wallet

        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Wallet balance label
        self.balance_label = MDLabel(
            text=f"Wallet Balance: ${self.wallet.get_balance():.2f}",
            halign="center",
            theme_text_color="Secondary",
            font_style="H6"
        )
        main_layout.add_widget(self.balance_label)

        # Advertisement placeholder
        ad_label = MDLabel(
            text="Advertisement",
            halign="center",
            theme_text_color="Hint",
            font_style="Subtitle1"
        )
        main_layout.add_widget(ad_label)

        # Coupons and Points buttons
        buttons_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height='120dp')
        self.coupons_button = MDRaisedButton(
            text="Coupons",
            size_hint=(1, None),
            height='50dp'
        )
        self.points_button = MDRaisedButton(
            text="Points",
            size_hint=(1, None),
            height='50dp'
        )
        buttons_layout.add_widget(self.coupons_button)
        buttons_layout.add_widget(self.points_button)
        main_layout.add_widget(buttons_layout)

        # Bottom buttons for "Generate Receipt" and "Add Items"
        bottom_buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height='60dp')
        self.generate_receipt_button = MDRaisedButton(
            text="Generate Receipt",
            size_hint=(0.5, 1),
            on_release=lambda x: self.app.generate_receipt()
        )
        self.add_items_button = MDRaisedButton(
            text="Add Items",
            size_hint=(0.5, 1),
            on_release=lambda x: self.app.switch_to_scanner()
        )
        bottom_buttons_layout.add_widget(self.generate_receipt_button)
        bottom_buttons_layout.add_widget(self.add_items_button)
        main_layout.add_widget(bottom_buttons_layout)

        self.add_widget(main_layout)

# Class for displaying the camera feed and scanning barcodes
class CameraPreview(Image):
    def __init__(self, capture, parent_screen, fps=30, **kwargs):
        """Initializes the camera preview widget."""
        super().__init__(**kwargs)
        self.capture = capture
        self.parent_screen = parent_screen
        self.fps = fps
        Clock.schedule_interval(self.update, 1.0 / self.fps)

    def update(self, dt):
        """Updates the camera feed and scans for barcodes."""
        if not self.capture.isOpened():
            print("Error: Camera is not opened.")
            return
        
        ret, frame = self.capture.read()
        if not ret:
            print("Error: Failed to read from the camera.")
            return
        
        try:
            # Flip the frame to invert the camera feed
            frame = cv2.rotate(frame, cv2.ROTATE_180)  # Flip the frame both horizontally and vertically
            frame = cv2.flip(frame, 0)

            buf = frame.tobytes()

            if not self.texture or self.texture.size != (frame.shape[1], frame.shape[0]):
                from kivy.graphics.texture import Texture
                self.texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                self.texture.flip_vertical()
            self.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.canvas.ask_update()

            # Scan for barcodes
            decoded_objects = decode(frame)
            for obj in decoded_objects:
                print(f"Barcode detected: {obj.data.decode('utf-8')}")
                # Pass barcode data to the parent screen for processing
                self.parent_screen.process_barcode_data(obj.data.decode('utf-8'))
                break
        except Exception as e:
            print(f"An error occurred during frame update: {e}")

    def on_leave(self):
        """Releases the camera when leaving the screen."""
        if self.capture.isOpened():
            self.capture.release()
            print("Camera released.")

# Screen class for barcode scanning and payment processing
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
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Add the camera preview
        self.camera_preview = CameraPreview(capture=self.capture, parent_screen=self)
        layout.add_widget(self.camera_preview)

        self.add_widget(layout)

    def process_barcode_data(self, data):
        """Processes the barcode data and opens the item detail screen."""
        # Simulated product data for demonstration
        product_database = {
            "product123": {"name": "Product A", "price": 15.0},
            "product456": {"name": "Product B", "price": 20.0},
            "product789": {"name": "Product C", "price": 25.0}
        }
        product_info = product_database.get(data)
        if product_info:
            item_name = product_info["name"]
            item_price = product_info["price"]
            self.app.open_item_detail_screen(item_name, item_price)
        else:
            print("Product not found in the database.")

    def on_leave(self):
        """Releases the camera when leaving the screen."""
        if self.capture.isOpened():
            self.capture.release()
            print("Camera released.")

# Item detail screen class
class ItemDetailScreen(Screen):
    def __init__(self, item_name, item_price, **kwargs):
        """Initializes the item detail screen."""
        super().__init__(**kwargs)
        self.item_name = item_name
        self.item_price = item_price
        self.quantity = 1  # Default quantity

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header layout with close button
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        item_label = MDLabel(text=f"Item: {self.item_name}", font_style="H5", halign="left")
        close_button = MDIconButton(icon="close", on_release=lambda x: self.close_screen())
        header_layout.add_widget(item_label)
        header_layout.add_widget(close_button)
        layout.add_widget(header_layout)

        # Price label
        price_label = MDLabel(text=f"Price: ${self.item_price:.2f}", font_style="Subtitle1", halign="left")
        layout.add_widget(price_label)

        # Quantity control layout
        quantity_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        decrease_button = MDRaisedButton(text="-", on_release=lambda x: self.update_quantity(-1))
        self.quantity_label = MDLabel(text=str(self.quantity), halign="center", font_style="H6")
        increase_button = MDRaisedButton(text="+", on_release=lambda x: self.update_quantity(1))

        quantity_layout.add_widget(decrease_button)
        quantity_layout.add_widget(self.quantity_label)
        quantity_layout.add_widget(increase_button)
        layout.add_widget(quantity_layout)

        # Ready to Go button
        ready_button = MDRaisedButton(text="Ready to Go", size_hint=(1, None), height='50dp')
        layout.add_widget(ready_button)

        self.add_widget(layout)

    def update_quantity(self, change):
        """Updates the quantity displayed."""
        new_quantity = self.quantity + change
        if new_quantity > 0:
            self.quantity = new_quantity
            self.quantity_label.text = str(self.quantity)

    def close_screen(self):
        """Closes the item detail screen."""
        self.manager.current = 'scanner'
        self.manager.remove_widget(self)

# Main app class
class MainApp(MDApp):
    def build(self):
        """Builds the main app and initializes the wallet."""
        self.wallet = Wallet(initial_balance=100.0)
        self.sm = ScreenManager()

        # Add the main screen
        main_screen = MainScreen(app=self, wallet=self.wallet, name='main')
        self.sm.add_widget(main_screen)

        # Add the QR code scanner screen
        scanner_screen = QRCodeScannerScreen(app=self, wallet=self.wallet, name='scanner')
        self.sm.add_widget(scanner_screen)

        return self.sm

    def switch_to_scanner(self):
        """Switches to the scanner screen."""
        self.sm.current = 'scanner'

    def open_item_detail_screen(self, item_name, item_price):
        """Opens the item detail screen."""
        item_screen = ItemDetailScreen(item_name=item_name, item_price=item_price, name='item_detail')
        self.sm.add_widget(item_screen)
        self.sm.current = 'item_detail'

    def generate_receipt(self):
        """Generates a PDF receipt from the transactions file."""
        if os.path.exists("transactions.txt"):
            try:
                from reportlab.pdfgen import canvas
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
