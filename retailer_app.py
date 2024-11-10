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
    "Coupon 1": 3,
    "Coupon 2": 2
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
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Wallet Management Button
        self.wallet_button = MDRaisedButton(
            text="Wallet",
            pos_hint={"center_x": 0.5},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.create_wallet()
        )
        layout.add_widget(self.wallet_button)

        # Inventory Management Button
        self.inventory_button = MDRaisedButton(
            text="Inventory",
            pos_hint={"center_x": 0.5},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.app.show_inventory_page()
        )
        layout.add_widget(self.inventory_button)

        # Coupon Management Button
        self.coupon_button = MDRaisedButton(
            text="Coupons",
            pos_hint={"center_x": 0.5},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.app.show_coupons_page()
        )
        layout.add_widget(self.coupon_button)

        # Suppliers Button
        self.suppliers_button = MDRaisedButton(
            text="Suppliers",
            pos_hint={"center_x": 0.5},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.show_suppliers()
        )
        layout.add_widget(self.suppliers_button)

        # Settings Button
        self.settings_button = MDRaisedButton(
            text="Settings",
            pos_hint={"center_x": 0.5},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.show_settings()
        )
        layout.add_widget(self.settings_button)

        self.add_widget(layout)

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

    def show_suppliers(self):
        """Displays a placeholder message for managing suppliers."""
        print("Suppliers management placeholder.")
        dialog = MDDialog(
            title="Suppliers",
            text="Manage your suppliers here. This is a placeholder for future implementation.",
            size_hint=(0.8, 0.5)
        )
        dialog.open()

    def show_settings(self):
        """Displays a placeholder message for settings management."""
        print("Settings management placeholder.")
        dialog = MDDialog(
            title="Settings",
            text="Access and modify app settings here. This is a placeholder for future implementation.",
            size_hint=(0.8, 0.5)
        )
        dialog.open()

# Screen class for displaying the inventory details
class InventoryPageScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Header Label
        header_label = MDLabel(text="Item", halign="left", font_style="H6")
        layout.add_widget(header_label)

        # Display inventory items
        for product_id, product in inventory.items():
            item_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height='40dp')
            item_label = MDLabel(text=product['name'], halign="left")
            stock_label = MDLabel(text=str(product['stock']), halign="center")
            item_layout.add_widget(item_label)
            item_layout.add_widget(stock_label)
            layout.add_widget(item_layout)

        # Analysis button
        analysis_button = MDRaisedButton(
            text="Analysis",
            pos_hint={"center_x": 0.5},
            size_hint=(0.6, 0.1),
            on_release=self.open_analysis_page
        )
        layout.add_widget(analysis_button)

        self.add_widget(layout)

    def open_analysis_page(self, instance):
        """Opens the analysis page."""
        self.manager.current = 'analysis_page'

# Screen class for displaying the coupon details and adding a new coupon
class CouponsPageScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Display coupon details
        for coupon_name, coupon_value in coupons.items():
            coupon_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height='40dp')
            coupon_label = MDLabel(text=coupon_name, halign="left")
            coupon_value_label = MDLabel(text=str(coupon_value), halign="center")
            coupon_layout.add_widget(coupon_label)
            coupon_layout.add_widget(coupon_value_label)
            layout.add_widget(coupon_layout)

        # Add Coupon button
        add_coupon_button = MDRaisedButton(
            text="Add Coupon",
            size_hint=(1, None),
            height='50dp'
        )
        layout.add_widget(add_coupon_button)

        self.add_widget(layout)

# Screen class for displaying the top sold items (Analysis Page)
class AnalysisPageScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Header Label
        header_label = MDLabel(text="Top Items Sold", halign="center", font_style="H5")
        layout.add_widget(header_label)

        # Item details
        items_sold = {
            "Apple": 100,
            "Banana": 50,
            "Chips": 30
        }

        for item_name, sold_count in items_sold.items():
            item_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height='40dp')
            item_label = MDLabel(text=item_name, halign="left")
            sold_label = MDLabel(text=f"Sold: {sold_count}", halign="right")
            item_layout.add_widget(item_label)
            item_layout.add_widget(sold_label)
            layout.add_widget(item_layout)

        self.add_widget(layout)

# Main app class for managing the retailer's app
class RetailerApp(MDApp):
    def build(self):
        self.sm = ScreenManager()
        retailer_screen = RetailerManagementScreen(app=self, name='retailer')
        self.sm.add_widget(retailer_screen)

        # Add screens for inventory, coupons, and analysis
        self.sm.add_widget(InventoryPageScreen(name='inventory_page'))
        self.sm.add_widget(CouponsPageScreen(name='coupons_page'))
        self.sm.add_widget(AnalysisPageScreen(name='analysis_page'))

        return self.sm

    def show_inventory_page(self):
        """Opens the inventory page screen."""
        self.sm.current = 'inventory_page'

    def show_coupons_page(self):
        """Opens the coupons page screen."""
        self.sm.current = 'coupons_page'

    def show_analysis_page(self):
        """Opens the analysis page screen."""
        self.sm.current = 'analysis_page'

# Run the app
if __name__ == '__main__':
    RetailerApp().run()
