from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout

# Simulated database for products and coupons
inventory = {
    "product123": {"name": "Product A", "price": 15.0, "stock": 10},
    "product456": {"name": "Product B", "price": 20.0, "stock": 5},
    "product789": {"name": "Product C", "price": 25.0, "stock": 8}
}

coupons = {
    "DISCOUNT10": {"description": "10% off", "discount_percent": 10},
    "FREESHIP": {"description": "Free Shipping", "discount_percent": 0}  # Example of non-monetary benefit
}

# Wallet class for customer wallets
class Wallet:
    def __init__(self, initial_balance=100.0):
        """Initializes the wallet with a starting balance."""
        self.balance = initial_balance

    def get_balance(self):
        """Returns the current balance."""
        return self.balance

    def add_balance(self, amount):
        """Adds the specified amount to the wallet."""
        self.balance += amount

# Screen class for managing retailer's inventory, wallets, and coupons
class RetailerManagementScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Inventory Management Button
        self.inventory_button = MDRaisedButton(
            text="Manage Inventory",
            pos_hint={"center_x": 0.5},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.show_inventory()
        )
        layout.add_widget(self.inventory_button)

        # Wallet Management Button
        self.wallet_button = MDRaisedButton(
            text="Create Wallet for Customer",
            pos_hint={"center_x": 0.5},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.create_wallet()
        )
        layout.add_widget(self.wallet_button)

        # Coupon Management Button
        self.coupon_button = MDRaisedButton(
            text="Manage Coupons",
            pos_hint={"center_x": 0.5},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.show_coupons()
        )
        layout.add_widget(self.coupon_button)

        self.add_widget(layout)

    def show_inventory(self):
        """Displays the current inventory and allows management."""
        inventory_list = "\n".join(
            [f"{product_id}: {product['name']} - ${product['price']} (Stock: {product['stock']})" for product_id, product in inventory.items()]
        )
        print("Inventory:")
        print(inventory_list)
        dialog = MDDialog(
            title="Inventory",
            text=inventory_list,
            size_hint=(0.8, 0.5)
        )
        dialog.open()

    def create_wallet(self):
        """Creates a wallet for a new customer."""
        dialog = MDDialog(
            title="Create Customer Wallet",
            type="custom",
            content_cls=MDTextField(hint_text="Enter initial balance"),
            buttons=[
                MDRaisedButton(
                    text="Create",
                    on_release=lambda x: self.add_wallet(dialog)
                )
            ]
        )
        dialog.open()

    def add_wallet(self, dialog):
        """Adds a new wallet with the specified balance."""
        initial_balance = float(dialog.content_cls.text)
        new_wallet = Wallet(initial_balance)
        print(f"New wallet created with initial balance: ${new_wallet.get_balance():.2f}")
        dialog.dismiss()

    def show_coupons(self):
        """Displays the current coupons and allows management."""
        coupons_list = "\n".join(
            [f"{code}: {coupon['description']} - {coupon['discount_percent']}% off" for code, coupon in coupons.items()]
        )
        print("Coupons:")
        print(coupons_list)
        dialog = MDDialog(
            title="Coupons",
            text=coupons_list,
            size_hint=(0.8, 0.5)
        )
        dialog.open()

# Main app class for managing the retailer's app
class RetailerApp(MDApp):
    def build(self):
        sm = ScreenManager()
        retailer_screen = RetailerManagementScreen(name='retailer')
        sm.add_widget(retailer_screen)
        return sm

# Run the app
if __name__ == '__main__':
    RetailerApp().run()
