# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 10:42:58 2023

@author: tungt
"""
import random
from datetime import date
import sys
# Item class
class Item: 
    def __init__(self, UPC, description, item_max_qty, order_threshold, replenishment_order_qty, item_on_hand, unit_price):
        self.UPC = UPC
        self.description = description
        self.item_max_qty = item_max_qty
        self.order_threshold = order_threshold
        self.replenishment_order_qty = replenishment_order_qty
        self.item_on_hand = item_on_hand
        self.unit_price = unit_price
        
    def update_unit_on_hand(self, numOfItems):
        self.item_on_hand += numOfItems

# Inventory class
class Inventory:
    def __init__(self, filePath):
        self.filePath = filePath
        self.all_items_dict = self.create_all_items_dict() #create an attribute to store all the results from create_all_items_dict method   
    
    def load_data(self):
        try:
           with open(self.filePath, 'r') as f:
               data = [line.strip().split(',') for line in f.readlines()]
           return data
        except:
           print("Unable to load data")
           return None
    
    def create_all_items_dict(self): 
        data = self.load_data()
        if data is not None:
            all_items_dict = {}
            for row in data:
                UPC = row[0]
                item = Item(UPC, row[1], float(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[6]))
                all_items_dict[UPC] = item
            return all_items_dict
        else:
            return {}
    
    def __getitem__(self, UPC):
        return self.all_items_dict.get(UPC)
    
    def __setitem__(self, UPC, item):
        if isinstance(item, Item):
            self.all_items_dict[UPC] = item
    
    #define a function to create an inventory report
    def create_inventory_report(self):
        print("** Inventory Report for Today **\n\n")
        print("__________________________________")
        for UPC, item in self.all_items_dict.items():
            print(f"Item: {item.description}")
            print(f"Quantity: {item.item_on_hand}")
            print(f"Order Threshold: {item.order_threshold}")        
# Sale class
class Sale:
    
    def __init__(self, inventory):
        self.items_dictionary = {}
        self.receipt_number = 0
        self.total_amount = 0
        self.used_receipts = {}
        self.daily_sales_report = {}
        self.monthly_sales_report = {}
        self.inventory = inventory
        
    def add_item(self, inventory, UPC, quantity):
        item = inventory[UPC]
        if item and item.item_on_hand >= quantity:
            self.items_dictionary[UPC] = self.items_dictionary.get(UPC, 0) + quantity
            item.update_unit_on_hand(-quantity) #deduct sale quantity from unit_on_hand
            self.calculate_total_amount(inventory) #update total amount
        
            #today sales data
            today = date.today()
            if today not in self.daily_sales_report:
                self.daily_sales_report[today] = {}
            if UPC in self.daily_sales_report[today]:
                self.daily_sales_report[today][UPC] += quantity
            else:
                self.daily_sales_report[today][UPC] = quantity
            
            #monthly sales data    
            current_month = (today.year, today.month)
            if current_month not in self.monthly_sales_report:
                self.monthly_sales_report[current_month] = {}
            if UPC in self.monthly_sales_report[current_month]:
                self.monthly_sales_report[current_month][UPC] += quantity
            else:
                self.monthly_sales_report[current_month][UPC] = quantity
        else:
            print("Item not found or insufficient quantity!")
            
    def create_receipt(self):
        receipt_number = random.randint(10000000, 99999999)
        self.used_receipts[receipt_number] = self.items_dictionary.copy()
        return receipt_number
        
    def calculate_total_amount(self, inventory):
        self.total_amount = 0
        for UPC, quantity in self.items_dictionary.items():
            self.total_amount += inventory[UPC].unit_price * quantity
        
    def view_cart(self, inventory):
        for UPC, quantity in self.items_dictionary.items():
            item = inventory[UPC]
            print(f"Item: {item.description}")
            print(f"Quantity: {quantity}")
            print(f"Unit Price: {item.unit_price}")
            print(f"Total Price: {item.unit_price * quantity}")
            print("---------------------")
        print(f"Total Amount: {self.total_amount}")
    
    def cancel_sale(self, inventory):
        for UPC, quantity in self.items_dictionary.items():
            inventory[UPC].update_unit_on_hand(quantity)
        self.items_dictionary.clear()
        self.total_amount = 0
    
    def return_single_item(self, inventory, UPC, quantity):
        if UPC in self.items_dictionary and self.items_dictionary[UPC] >= quantity:
            self.items_dictionary[UPC] -= quantity
            inventory[UPC].update_unit_on_hand(quantity)
            self.total_amount -= inventory[UPC].unit_price * quantity
            print("You returned: ", inventory[UPC].description, "Quantity: ", quantity)
            print("Return amount: ", inventory[UPC].unit_price * quantity)
        else:
            print("Item not found or excessive return quantity!")
    
    def return_all_item(self, inventory, receipt_number):
        returned_items = self.used_receipts.get(receipt_number, {})
        if returned_items:
            return_amount = 0
            for UPC, quantity in returned_items.items():
                inventory[UPC].update_unit_on_hand(quantity)
                return_amount += inventory[UPC].unit_price * quantity
                print("You returned: ", inventory[UPC].description, "Quantity: ", quantity)
            self.total_amount -= return_amount
            print("Return Amount: ", return_amount)
        else:
            print("Invalid receipt number!")
    
    #define today sales report
    def print_today_sales_report(self, inventory):
        today = date.today()
        if today in self.daily_sales_report:
            print(f"** Sales report for {today} **")
            print("_______________________________")
            total_sales = 0 
            for UPC, quantity in self.daily_sales_report[today].items():
                print(f"Item: {UPC}, Quantity sold: {quantity}")
                total_sales += quantity * self.inventory[UPC].unit_price
            print(f"Total sales: {total_sales}")
        else:
            print(f"No sales for {today}.")
    
    #define monthly sales report
    def print_monthly_sales_report(self, inventory, year, month):
        sales_month = (year, month)
        if sales_month in self.monthly_sales_report:
            print(f"** {sales_month} Sales Report **")
            print("_______________________________")
            total_sales = 0
            for UPC, quantity in self.monthly_sales_report[sales_month].items():
                print(f"Item: {UPC}, Quantity sold: {quantity}")
                total_sales += quantity * inventory[UPC].unit_price
            print(f"Total sales: {total_sales}")
        else:
            print(f"No sales for {sales_month}")
            
class POS:
    def __init__(self):
        self.ui_pass_dict = self.get_all_user_id_password_data()
        self.inventory = None

    @staticmethod
    def get_all_user_id_password_data():
        ui_pass_dict = {}
        with open("C:/Users/tungt/OneDrive/Desktop/SEIS603-Python/UserIDPassword.txt", 'r') as password_file:
            for line in password_file:
                user_id, password = line.split()
                ui_pass_dict[user_id] = password
        return ui_pass_dict

    def verify_ui_and_pw(self, user_id, password):
        return self.ui_pass_dict.get(user_id) == password

    def run(self):
        print("Welcome to the POS System\n\n")

        for _ in range(3):  # give the user 3 times to login
            user_id = input("Please enter userid: ")
            password = input("Please enter password: ")

            if self.verify_ui_and_pw(user_id, password):
                print(f"Welcome {user_id} to the POS System!")
                self.inventory = Inventory(r"C:\Users\tungt\OneDrive\Desktop\SEIS603-Python\RetailStoreItemData-1.txt - Copy.txt")
                self.sale = Sale(self.inventory)
                break
            else:
                print("The userID and password you entered does not match any account on record. Please, re-enter.")
        else:
            print(f"{user_id}. Your account has been locked out. Please contact your system admin for supports.")
            sys.exit()  # exit the program after 3 failed login attempts

        while True:
            try:
                option = int(input("\n Please select your option:\n1 = New Sale, 2 = Return Item/s, 3 = Inventory Report, 4 = Today Sales Report, 5 = Monthly Sales Report 9 = Exit Application\tPlease, select your option:\n")) 
            except ValueError:
                print("Invalid input!")
                continue

            if option == 1:
                self.new_sale()
            elif option == 2:
                self.handle_return()
            elif option == 3:
                self.inventory.create_inventory_report()
            elif option == 4:
                self.sale.print_today_sales_report(self.inventory)
            elif option == 5:
                year = int(input("Please enter the year:\n"))
                month = int(input("Please enter the month:\n"))
                self.sale.print_monthly_sales_report(self.inventory, year, month)
            elif option == 9:
                print("Exit Application.")
                break
            else:
                print("Invalid option!")

    def new_sale(self):
        while True:
            UPC = input("Please enter the UPC:\n")
            quantity = int(input("Please enter quantity:\n"))
            self.sale.add_item(self.inventory, UPC, quantity)
            print("The price is: ", self.inventory[UPC].unit_price * quantity)

            print("1 = Sell another item, 2 = Cancel Sale, 3 = View Cart, 9 = Complete Sale")
            sale_option = int(input("Please select your option: "))

            if sale_option == 1:
                continue
            elif sale_option == 2:
                self.sale.cancel_sale(self.inventory)
                print("Your sale has been cancelled.")
                break
            elif sale_option == 3:
                self.sale.view_cart(self.inventory)
            elif sale_option == 9:
                receipt_number = self.sale.create_receipt()
                print("Your receipt number is:\n", receipt_number)
                print("Your total is:\n", self.sale.total_amount)
                break
            else:
                print("Invalid option!")

    def handle_return(self):
        receipt_number = int(input("Please, Enter the receipt number:\n"))
        return_option = int(input("1 - Return Single Item, 2 - Return All Items"))
        if return_option == 1:
            UPC = input("Please enter the UPC:\n")
            quantity = int(input("Please enter quantity:\n"))
            self.sale.return_single_item(self.inventory, UPC, quantity)
        elif return_option == 2:
            return_all = input("Are you sure you want to return all items? Y/N\n")
            if return_all.lower() == 'y':
                self.sale.return_all_item(self.inventory, receipt_number)


if __name__ == "__main__":
    pos = POS()
    pos.run()
 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    