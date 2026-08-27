import pandas as pd
from datetime import datetime


class MenuItem:

    def __init__(self,item_id,category,name,price):
        self.item_id=item_id
        self.category=category
        self.name=name
        self.price=price
    def __str__(self):
        return f"{self.item_id} - {self.name} - {self.price:.2f}"

    ######### MENU ################
class Menu :
    def __init__(self) :
        menu_data={
            "Category":[
                "Pizza",
                "Pizza",
                "Pizza",

                "Burger",
                "Burger",
                "Burger",

                "Sandwich",
                "Sandwich",
                "Sandwich",

                "Fries",
                "Fries"

            ],

            "Item":[
                "Margrita",
                "chicken runch",
                "BBQ",

                "Cheese Burger",
                "Chicken Burger",
                "Classic Burger",

                "Hotdog",
                "Chicken Burger",
                "Chicken Crisby",

                "Classic fries",
                "Cheese fries"

            ],

            "Price":[
                35.00,
                55.00,
                60.00,

                35.00,
                55.00,
                60.00,

                35.00,
                55.00,
                60.00,

                20.00,
                30.00

            ]
        } 
    
        self.menu=pd.DataFrame(menu_data)

        self.menu.insert(
            0,
            "Item_ID",
            range(1,len(self.menu)+1)
        )
    def display(self):

        print("\n" + "=" * 55)
        print("                 RESTAURANT MENU")
        print("=" * 55)

        print(self.menu.to_string(index=False))

        print("=" * 55)
    def show_category(self, category):

        result = self.menu[
            self.menu["Category"].str.lower() == category.lower()
        ]

        if result.empty:

            print("Category not found.")

        else:

            print(f"\n-- {category.upper()} --")
            print(result.to_string(index=False))


    def search_item(self, item_name):

        result = self.menu[
            self.menu["Item"].str.contains(
                item_name,
                case=False,
                na=False
            )
        ]

        if result.empty:

            print("Item not found.")

        else:

            print("\nSearch Result:")
            print(result.to_string(index=False))



########### Table ############

class Table:

    def __init__(self,table_id,capacity):
        self.table_id=table_id
        self.capacity=capacity
        self.status="available"

    def reserve(self):

        if self.status=="available":
            self.status="reserved"
            return True
        return False
    def occupy(self):

        if self.status == "reserved":

            self.status = "occupied"

            return True

        return False
    
    def free(self):

        self.status = "available"

    def __str__(self):

        return (
            f"Table {self.table_id} | "
            f"Capacity: {self.capacity} | "
            f"Status: {self.status}"
        )
 ############ reservation #########
    
class Reservation:

    def __init__( self, reservation_id,customer_id,table_id,date,time,number_of_people):

        self.reservation_id = reservation_id
        self.customer_id = customer_id
        self.table_id = table_id
        self.date = date
        self.time = time
        self.number_of_people = number_of_people
        self.status = "confirmed"
        self.created_at = datetime.now()

    def cancel(self):

        self.status="cancelled"

    def __str__(self):

        return (
            f"Reservation ID: {self.reservation_id}\n"
            f"Customer ID: {self.customer_id}\n"
            f"Table ID: {self.table_id}\n"
            f"Date: {self.date}\n"
            f"Time: {self.time}\n"
            f"People: {self.number_of_people}\n"
            f"Status: {self.status}"
        )
    ############# resturant ############
class Restaurant:
    def __init__(self, name, number_of_tables):

        self.name = name

        self.menu = Menu()

        self.tables = {}

        for i in range(1, number_of_tables + 1):

            if i % 3 == 0:
                capacity = 6

            elif i % 2 == 0:
                capacity = 4

            else:
                capacity = 2

            self.tables[i] = Table(
                table_id=i,
                capacity=capacity
            )
        self.reservations = {}

        self.next_reservation_id = 1

    def display_menu(self):

        self.menu.display()

    def search_menu(self, item_name):

        self.menu.search_item(item_name)

    def show_category(self, category):

        self.menu.show_category(category)

    def show_all_tables(self):

        print("\n" + "=" * 50)
        print("                 TABLES")
        print("=" * 50)

        for table in self.tables.values():

            print(table)

        print("=" * 50)

    def show_available_tables(self):

        print("\nAvailable Tables:")

        found = False

        for table in self.tables.values():

            if table.status == "available":

                print(table)
                found = True

        if not found:

            print("No available tables.")


    def find_available_table(self, number_of_people):

        for table in self.tables.values():

            if (
                table.status == "available"
                and table.capacity >= number_of_people
            ):

                return table

        return None
    
    def make_reservation(self,customer_id,date,time,number_of_people):

        table = self.find_available_table(number_of_people)

        if table is None:

            print(
                "Sorry, there is no available table "
                "for this number of people."
            )

            return None
        table.reserve()

        reservation = Reservation(
            reservation_id=self.next_reservation_id,
            customer_id=customer_id,
            table_id=table.table_id,
            date=date,
            time=time,
            number_of_people=number_of_people
        )

        self.reservations[
            self.next_reservation_id
        ] = reservation

        print("\nReservation successful!")
        print(reservation)
        self.next_reservation_id += 1
        return reservation
    
    def cancel_reservation(self, reservation_id):

        if reservation_id not in self.reservations:

            print("Reservation not found.")
            return False

        reservation = self.reservations[reservation_id]

        if reservation.status == "cancelled":

            print("Reservation is already cancelled.")
            return False
        
        reservation.cancel()

        table=self.tables[reservation.table_id]
        table.free()

        print ("Reservation cancelled successfully")

        return True
    def show_reservations(self):

        print("\n" + "=" * 50)
        print("              RESERVATIONS")
        print("=" * 50)

        if not self.reservations:

            print("No reservations.")

            return

        for reservation in self.reservations.values():

            print(reservation)
            print("-" * 50)
if __name__ == "__main__":

    restaurant = Restaurant(
        name="AI Restaurant",
        number_of_tables=10
    )
    restaurant.display_menu()

    restaurant.search_menu("Chicken")    

    restaurant.show_category("Burger")

    restaurant.show_all_tables()

    restaurant.show_available_tables()

    reservation = restaurant.make_reservation(
        customer_id=101,
        date="25/08/2026",
        time="07:00 PM",
        number_of_people=4
    )

    restaurant.show_all_tables()

    restaurant.show_reservations()

    if reservation:

        restaurant.cancel_reservation(
            reservation.reservation_id
        )
    restaurant.show_available_tables()   