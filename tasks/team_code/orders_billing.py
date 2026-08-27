
from datetime import datetime
class OrderItem:
    def __init__(self, item_id, name, price, quantity):
        self.item_id = item_id
        self.name = name
        self.price = price
        self.quantity = quantity
    def get_total(self):
        return self.price * self.quantity
class Order:
    def __init__(self, order_id, customer_id):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items = []
        self.total_price = 0
        self.status = "pending"
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    def add_item_to_order(self, item_id, name, price, quantity):
        if quantity <= 0:
            print("Pls Enter correct quantity")
            return False
        for item in self.items:
            if item.item_id == item_id:
                item.quantity += quantity
                self.calculate_total()
                return True
        new_item = OrderItem(
            item_id,
            name,
            price,
            quantity
        )
        self.items.append(new_item)
        self.calculate_total()
        return True
    def remove_item_from_order(self, item_id):
        for item in self.items:
            if item.item_id == item_id:
                self.items.remove(item)
                self.calculate_total()
                return True
        return False
    def calculate_total(self):
        self.total_price = 0
        for item in self.items:
            self.total_price += item.get_total()
        return self.total_price
    def update_order_status(self, status):
        valid_statuses = [
            "pending",
            "preparing",
            "ready",
            "delivered",
            "cancelled"
        ]
        if status in valid_statuses:
            self.status = status
            return True
        return False
    def get_order_status(self):
        return self.status
    def show_order(self):
        print("\n==========** Order **==========")
        print("Order ID:", self.order_id)
        print("Customer ID:", self.customer_id)
        print("Status:", self.status)
        print("Created At:", self.created_at)
        print("=====================")
        if len(self.items) == 0:
            print("No items")
        else:
            for item in self.items:
                print(
                    item.name,
                    "| Quantity:",
                    item.quantity,
                    "| Price:",
                    item.price,
                    "| Total:",
                    item.get_total()
                )
        print("===========================")
        print("Total Price:", self.total_price)
        print("===========================")
class OrderSystem:
    def __init__(self):
        self.orders = []
        self.next_order_id = 1
    def create_order(self, customer_id):
        order = Order(
            self.next_order_id,
            customer_id
        )
        self.orders.append(order)
        self.next_order_id += 1
        return order
    def get_order(self, order_id):
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None
    def create_invoice(self, order_id):
        order = self.get_order(order_id)
        if order is None:
            return None
        invoice = InvoiceSystem()
        return invoice.create_invoice(order)
class Invoice:
    def __init__(
        self,
        invoice_id,
        order_id,
        subtotal,
        tax,
        discount,
        total,
        payment_status
    ):
        self.invoice_id = invoice_id
        self.order_id = order_id
        self.subtotal = subtotal
        self.tax = tax
        self.discount = discount
        self.total = total
        self.payment_status = payment_status
    def show_invoice(self):
        print("\n========== ***Invoice*** ==========")
        print("Invoice ID:", self.invoice_id)
        print("Order ID:", self.order_id)
        print("Subtotal:", self.subtotal)
        print("Tax:", self.tax)
        print("Discount:", self.discount)
        print("Total:", self.total)
        print("Payment Status:", self.payment_status)
        print("=============================")
class InvoiceSystem:
    def __init__(self):
        self.next_invoice_id = 1
    def create_invoice(
        self,
        order,
        tax_rate=0.14,
        discount=0
    ):
        subtotal = order.calculate_total()
        if discount < 0:
            discount = 0
        if discount > subtotal:
            discount = subtotal
        taxable_amount = subtotal - discount
        tax = taxable_amount * tax_rate
        total = taxable_amount + tax
        invoice = Invoice(
            self.next_invoice_id,
            order.order_id,
            subtotal,
            tax,
            discount,
            total,
            "unpaid"
        )
        self.next_invoice_id += 1
        return invoice
    def update_payment_status(
        self,
        invoice,
        payment_status
    ):
        valid_statuses = [
            "unpaid",
            "paid",
            "failed"
        ]

        if payment_status in valid_statuses:
            invoice.payment_status = payment_status
            return True
        return False
def create_order(order_system, customer_id):
    return order_system.create_order(customer_id)
def add_item_to_order(
    order,
    item_id,
    name,
    price,
    quantity
):
    return order.add_item_to_order(
        item_id,
        name,
        price,
        quantity
    )
def remove_item_from_order(order, item_id):
    return order.remove_item_from_order(item_id)
def calculate_total(order):
    return order.calculate_total()
def update_order_status(order, status):
    return order.update_order_status(status)
def get_order_status(order):
    return order.get_order_status()
def create_invoice(order_system, order_id):
    return order_system.create_invoice(order_id)