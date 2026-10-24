"""
Interactive Console Menu Interface for Medicine Store Management System.
Implements the 11-option menu system described in the system architecture.
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.store import MedicineStoreManagementSystem
from backend.exceptions import MedicineStoreError


def print_header(title: str):
    print("\n" + "=" * 55)
    print(f"  {title}")
    print("=" * 55)


def medicine_menu(store: MedicineStoreManagementSystem):
    while True:
        print_header("MEDICINE MANAGEMENT")
        print("1. Add New Medicine")
        print("2. View All Medicines")
        print("3. Search Medicine (by ID or Name)")
        print("4. Update Medicine")
        print("5. Delete Medicine")
        print("6. Back to Main Menu")

        choice = input("\nEnter choice (1-6): ").strip()
        if choice == "1":
            try:
                name = input("Medicine Name: ").strip()
                company = input("Company: ").strip()
                category = input("Category: ").strip()
                price = float(input("Price (Rs.): ").strip() or "0")
                qty = int(input("Quantity: ").strip() or "0")
                exp = input("Expiry Date (YYYY-MM-DD): ").strip()
                rx = input("Requires Prescription? (y/N): ").strip().lower() == 'y'

                med = store.add_medicine({
                    "name": name, "company": company, "category": category,
                    "price": price, "quantity": qty, "expiry_date": exp,
                    "requires_prescription": rx
                })
                print(f"\n[SUCCESS] Added medicine: {med.display_medicine()}")
            except Exception as e:
                print(f"[ERROR] {e}")

        elif choice == "2":
            meds = list(store.medicines.values())
            print(f"\nTotal Medicines: {len(meds)}")
            print("-" * 75)
            print(f"{'ID':<10}{'Name':<25}{'Price':<10}{'Stock':<8}{'Expiry':<14}{'Rx':<5}")
            print("-" * 75)
            for m in meds:
                print(f"{m.medicine_id:<10}{m.name[:23]:<25}Rs.{m.price:<7.2f}{m.quantity:<8}{m.expiry_date:<14}{'Yes' if m.requires_prescription else 'No':<5}")

        elif choice == "3":
            query = input("Enter Medicine Name or ID to search: ").strip().lower()
            results = [m for m in store.medicines.values() if query in m.name.lower() or query in m.medicine_id.lower()]
            if not results:
                print(f"No medicines matching '{query}'.")
            else:
                for m in results:
                    print(f"- {m.display_medicine()}")

        elif choice == "4":
            mid = input("Enter Medicine ID to update: ").strip()
            med = store.medicines.get(mid)
            if not med:
                print(f"Medicine '{mid}' not found.")
                continue
            print(f"Editing {med.name} (leave blank to keep current):")
            name = input(f"New Name [{med.name}]: ").strip()
            price_str = input(f"New Price [{med.price}]: ").strip()
            qty_str = input(f"New Quantity [{med.quantity}]: ").strip()
            exp = input(f"New Expiry [{med.expiry_date}]: ").strip()

            update_data = {}
            if name: update_data["name"] = name
            if price_str: update_data["price"] = float(price_str)
            if qty_str: update_data["quantity"] = int(qty_str)
            if exp: update_data["expiry_date"] = exp

            store.update_medicine(mid, update_data)
            print("[SUCCESS] Medicine updated.")

        elif choice == "5":
            mid = input("Enter Medicine ID to delete: ").strip()
            try:
                store.delete_medicine(mid)
                print(f"[SUCCESS] Deleted medicine '{mid}'.")
            except Exception as e:
                print(f"[ERROR] {e}")

        elif choice == "6":
            break


def supplier_menu(store: MedicineStoreManagementSystem):
    while True:
        print_header("SUPPLIER MANAGEMENT")
        print("1. Register New Supplier")
        print("2. List All Suppliers")
        print("3. Back to Main Menu")

        choice = input("\nEnter choice (1-3): ").strip()
        if choice == "1":
            try:
                name = input("Supplier Contact Name: ").strip()
                company = input("Company Name: ").strip()
                mobile = input("Mobile Number: ").strip()
                addr = input("Address: ").strip()
                sup = store.add_supplier({"name": name, "company": company, "mobile": mobile, "address": addr})
                print(f"[SUCCESS] Supplier added: {sup.display_details()}")
            except Exception as e:
                print(f"[ERROR] {e}")
        elif choice == "2":
            print(f"\nRegistered Suppliers ({len(store.suppliers)}):")
            for s in store.suppliers.values():
                print(f"- {s.display_details()}")
        elif choice == "3":
            break


def customer_menu(store: MedicineStoreManagementSystem):
    while True:
        print_header("CUSTOMER MANAGEMENT")
        print("1. Register New Customer")
        print("2. List Customers")
        print("3. View Customer Purchase History")
        print("4. Back to Main Menu")

        choice = input("\nEnter choice (1-4): ").strip()
        if choice == "1":
            try:
                name = input("Customer Name: ").strip()
                mobile = input("Mobile Number: ").strip()
                addr = input("Address: ").strip()
                cust = store.add_customer({"name": name, "mobile": mobile, "address": addr})
                print(f"[SUCCESS] Customer registered with ID: {cust.customer_id}")
            except Exception as e:
                print(f"[ERROR] {e}")
        elif choice == "2":
            print(f"\nRegistered Customers ({len(store.customers)}):")
            for c in store.customers.values():
                print(f"- {c.display_details()}")
        elif choice == "3":
            cid = input("Enter Customer ID: ").strip()
            cust = store.customers.get(cid)
            if not cust:
                print(f"Customer '{cid}' not found.")
            else:
                history = cust.view_purchase_history()
                print(f"\nPurchase History for {cust.name} ({len(history)} purchases):")
                for s in history:
                    print(f"  * Sale {s.get('sale_id')} on {s.get('sale_date')}: Total Rs.{s.get('total')}")
        elif choice == "4":
            break


def prescription_menu(store: MedicineStoreManagementSystem):
    while True:
        print_header("PRESCRIPTION MANAGEMENT")
        print("1. Add Prescription")
        print("2. List Prescriptions")
        print("3. Verify Prescription")
        print("4. Back to Main Menu")

        choice = input("\nEnter choice (1-4): ").strip()
        if choice == "1":
            try:
                doc = input("Doctor Name: ").strip()
                patient = input("Patient Name: ").strip()
                meds_str = input("Prescribed Medicines (comma-separated): ").strip()
                rx = store.add_prescription({
                    "doctor_name": doc, "patient_name": patient,
                    "prescribed_medicines": meds_str
                })
                print(f"[SUCCESS] Prescription registered: {rx.prescription_id}")
            except Exception as e:
                print(f"[ERROR] {e}")
        elif choice == "2":
            for p in store.prescriptions.values():
                print(f"- {p.display_prescription()}")
        elif choice == "3":
            pid = input("Enter Prescription ID to verify: ").strip()
            try:
                store.verify_prescription(pid)
                print(f"[SUCCESS] Prescription {pid} verified.")
            except Exception as e:
                print(f"[ERROR] {e}")
        elif choice == "4":
            break


def sales_menu(store: MedicineStoreManagementSystem):
    while True:
        print_header("SALES MANAGEMENT")
        print("1. Process New Sale")
        print("2. View All Sales")
        print("3. Back to Main Menu")

        choice = input("\nEnter choice (1-3): ").strip()
        if choice == "1":
            try:
                cid = input("Enter Customer ID (or leave blank for Walk-in): ").strip() or "WALKIN"
                rx_id = input("Prescription ID (optional): ").strip() or None

                items = []
                while True:
                    mid = input("Enter Medicine ID (or 'done' to finish): ").strip()
                    if mid.lower() in ("done", ""):
                        break
                    med = store.medicines.get(mid)
                    if not med:
                        print(f"Medicine '{mid}' not found!")
                        continue
                    print(f"Selected: {med.name} | Available: {med.quantity} | Rate: Rs.{med.price}")
                    qty = int(input(f"Enter quantity to buy: ").strip())
                    items.append({"medicine_id": mid, "quantity": qty})

                if not items:
                    print("No items added. Aborting sale.")
                    continue

                res = store.process_sale(cid, items, prescription_id=rx_id)
                print("\n" + res["bill"]["receipt_text"])
            except MedicineStoreError as e:
                print(f"\n[SALE REJECTED] {e.message}")
            except Exception as e:
                print(f"\n[ERROR] {e}")
        elif choice == "2":
            sales = store.sales
            print(f"\nTotal Sales Completed: {len(sales)}")
            for s in sales:
                print(f"- Sale {s.sale_id} | Cust: {s.customer_name} | Total: Rs.{s.total:.2f} | Date: {s.sale_date}")
        elif choice == "3":
            break


def inventory_menu(store: MedicineStoreManagementSystem):
    while True:
        print_header("INVENTORY MANAGEMENT")
        print("1. View Current Stock & Valuation")
        print("2. Check Low-Stock Alerts")
        print("3. Check Expired Medicines")
        print("4. Add Stock to Medicine")
        print("5. Back to Main Menu")

        choice = input("\nEnter choice (1-5): ").strip()
        if choice == "1":
            total_value = sum(m.price * m.quantity for m in store.medicines.values())
            print(f"\nTotal Stock Items: {len(store.medicines)} | Total Inventory Value: Rs.{total_value:,.2f}")
            for m in store.medicines.values():
                status = "[LOW STOCK]" if m.quantity <= m.reorder_level else "[OK]"
                if m.is_expired(): status = "[EXPIRED]"
                print(f"{status:<12} {m.medicine_id:<10} {m.name:<24} Stock: {m.quantity:<6} Value: Rs.{m.price*m.quantity:.2f}")
        elif choice == "2":
            low = store.inventory.check_low_stock()
            print(f"\nLow Stock Items ({len(low)}):")
            for m in low:
                print(f"⚠️  {m.name} (ID: {m.medicine_id}) - In Stock: {m.quantity} (Reorder Level: {m.reorder_level})")
        elif choice == "3":
            exp = store.inventory.check_expired_medicines()
            print(f"\nExpired Items ({len(exp)}):")
            for m in exp:
                print(f"⛔ {m.name} (ID: {m.medicine_id}) - Expired on: {m.expiry_date}")
        elif choice == "4":
            mid = input("Enter Medicine ID: ").strip()
            qty = int(input("Quantity to add: ").strip())
            try:
                med = store.adjust_stock(mid, qty)
                print(f"[SUCCESS] Stock updated. New stock for {med.name}: {med.quantity}")
            except Exception as e:
                print(f"[ERROR] {e}")
        elif choice == "5":
            break


def billing_menu(store: MedicineStoreManagementSystem):
    while True:
        print_header("BILLING & PAYMENT MANAGEMENT")
        print("1. View All Invoices / Bills")
        print("2. Reprint Receipt by Bill ID")
        print("3. Back to Main Menu")

        choice = input("\nEnter choice (1-3): ").strip()
        if choice == "1":
            print(f"\nTotal Bills ({len(store.bills)}):")
            for b in store.bills.values():
                print(f"Bill #{b.bill_id} | Date: {b.bill_date} | Customer: {b.customer_name} | Total: Rs.{b.total_amount:.2f}")
        elif choice == "2":
            bid = input("Enter Bill ID: ").strip()
            bill = store.bills.get(bid)
            if not bill:
                print(f"Bill '{bid}' not found.")
            else:
                print("\n" + bill.print_bill())
        elif choice == "3":
            break


def report_menu(store: MedicineStoreManagementSystem):
    while True:
        print_header("REPORT GENERATION")
        print("1. Summary Dashboard Metrics")
        print("2. Export Medicines to CSV")
        print("3. Export Sales to CSV")
        print("4. Back to Main Menu")

        choice = input("\nEnter choice (1-4): ").strip()
        if choice == "1":
            dash = store.get_dashboard_summary()
            print("\nSTORE DASHBOARD SUMMARY:")
            print(f"Total Medicines  : {dash['medicines']}")
            print(f"Total Customers  : {dash['customers']}")
            print(f"Total Suppliers  : {dash['suppliers']}")
            print(f"Total Invoices   : {dash['bills']}")
            print(f"Total Revenue    : Rs.{dash['revenue']:,.2f}")
            print(f"Low Stock Alerts : {dash['low_stock_count']}")
            print(f"Expired Medicines: {dash['expired_count']}")
        elif choice == "2":
            csv_str = store.export_csv_data("medicines")
            path = os.path.join(store.data_dir, "medicines_report.csv")
            with open(path, "w", encoding="utf-8") as f:
                f.write(csv_str)
            print(f"[SUCCESS] Medicines report exported to: {path}")
        elif choice == "3":
            csv_str = store.export_csv_data("sales")
            path = os.path.join(store.data_dir, "sales_report.csv")
            with open(path, "w", encoding="utf-8") as f:
                f.write(csv_str)
            print(f"[SUCCESS] Sales report exported to: {path}")
        elif choice == "4":
            break


def main_menu():
    store = MedicineStoreManagementSystem()

    while True:
        print("\n" + "=" * 55)
        print("     MEDICINE STORE MANAGEMENT SYSTEM (CLI)     ")
        print("=" * 55)
        print("1.  Medicine Management")
        print("2.  Supplier Management")
        print("3.  Customer Management")
        print("4.  Prescription Management")
        print("5.  Sales Management")
        print("6.  Inventory Management")
        print("7.  Billing & Payment Management")
        print("8.  Report Generation")
        print("9.  Save Data")
        print("10. Load Data")
        print("11. Exit")
        print("=" * 55)

        choice = input("\nEnter your choice (1-11): ").strip()

        if choice == "1":
            medicine_menu(store)
        elif choice == "2":
            supplier_menu(store)
        elif choice == "3":
            customer_menu(store)
        elif choice == "4":
            prescription_menu(store)
        elif choice == "5":
            sales_menu(store)
        elif choice == "6":
            inventory_menu(store)
        elif choice == "7":
            billing_menu(store)
        elif choice == "8":
            report_menu(store)
        elif choice == "9":
            store.save_data()
            print("\n[SUCCESS] All store records saved to JSON files.")
        elif choice == "10":
            store.load_data()
            print("\n[SUCCESS] Data refreshed from JSON storage.")
        elif choice == "11":
            print("\nThank you for using Medicine Store Management System. Goodbye!")
            break
        else:
            print("\n[INVALID] Please select a valid option from 1 to 11.")


if __name__ == "__main__":
    main_menu()
