"""
Core System Controller: MedicineStoreManagementSystem.
Coordinates all entities, business workflows, transactions, validations,
file handling (JSON persistence), and CSV export capabilities.
"""

import os
import json
import uuid
import datetime
from typing import Dict, List, Any, Optional

from backend.models import (
    Customer,
    Supplier,
    Medicine,
    Inventory,
    Prescription,
    Sale,
    Bill,
    Report
)
from backend.exceptions import (
    MedicineNotFoundError,
    OutOfStockError,
    ExpiredMedicineError,
    InvalidCustomerError,
    InvalidSupplierError,
    InvalidQuantityError,
    InvalidPrescriptionError
)
from backend.utils import (
    log_action,
    sales_report_generator,
    export_to_csv_string
)
from backend.sample_data import (
    get_sample_medicines,
    get_sample_customers,
    get_sample_suppliers,
    get_sample_prescriptions
)


class MedicineStoreManagementSystem:
    """
    Central controller class implementing OOP Architecture and file persistence.
    """
    def __init__(self, data_dir: Optional[str] = None):
        if not data_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        self.medicines: Dict[str, Medicine] = {}
        self.customers: Dict[str, Customer] = {}
        self.suppliers: Dict[str, Supplier] = {}
        self.prescriptions: Dict[str, Prescription] = {}
        self.inventory: Inventory = Inventory("INV-MAIN")
        self.sales: List[Sale] = []
        self.bills: Dict[str, Bill] = {}

        self.load_data()

    # -------------------------------------------------------------
    # FILE PERSISTENCE (JSON)
    # -------------------------------------------------------------
    def _file_path(self, filename: str) -> str:
        return os.path.join(self.data_dir, filename)

    @log_action("Save Store Data")
    def save_data(self):
        """Serializes all in-memory entities into structured JSON files."""
        # 1. Medicines
        with open(self._file_path("medicines.json"), "w", encoding="utf-8") as f:
            json.dump([m.to_dict() for m in self.medicines.values()], f, indent=2)

        # 2. Customers
        with open(self._file_path("customers.json"), "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in self.customers.values()], f, indent=2)

        # 3. Suppliers
        with open(self._file_path("suppliers.json"), "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in self.suppliers.values()], f, indent=2)

        # 4. Prescriptions
        with open(self._file_path("prescriptions.json"), "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in self.prescriptions.values()], f, indent=2)

        # 5. Sales
        with open(self._file_path("sales.json"), "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in self.sales], f, indent=2)

        # 6. Bills
        with open(self._file_path("bills.json"), "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.bills.values()], f, indent=2)

    @log_action("Load Store Data")
    def load_data(self):
        """Loads entities from JSON; populates sample data if store is empty."""
        # Reset state
        self.medicines.clear()
        self.customers.clear()
        self.suppliers.clear()
        self.prescriptions.clear()
        self.inventory = Inventory("INV-MAIN")
        self.sales.clear()
        self.bills.clear()

        # Load Medicines
        med_file = self._file_path("medicines.json")
        if os.path.exists(med_file) and os.path.getsize(med_file) > 2:
            try:
                with open(med_file, "r", encoding="utf-8") as f:
                    for d in json.load(f):
                        m = Medicine.from_dict(d)
                        self.medicines[m.medicine_id] = m
                        self.inventory.add_medicine(m)
            except Exception as e:
                print(f"[WARN] Error reading medicines.json: {e}")
        else:
            for d in get_sample_medicines():
                m = Medicine.from_dict(d)
                self.medicines[m.medicine_id] = m
                self.inventory.add_medicine(m)

        # Load Customers
        cust_file = self._file_path("customers.json")
        if os.path.exists(cust_file) and os.path.getsize(cust_file) > 2:
            try:
                with open(cust_file, "r", encoding="utf-8") as f:
                    for d in json.load(f):
                        c = Customer.from_dict(d)
                        self.customers[c.customer_id] = c
            except Exception as e:
                print(f"[WARN] Error reading customers.json: {e}")
        else:
            for d in get_sample_customers():
                c = Customer.from_dict(d)
                self.customers[c.customer_id] = c

        # Load Suppliers
        sup_file = self._file_path("suppliers.json")
        if os.path.exists(sup_file) and os.path.getsize(sup_file) > 2:
            try:
                with open(sup_file, "r", encoding="utf-8") as f:
                    for d in json.load(f):
                        s = Supplier.from_dict(d)
                        self.suppliers[s.supplier_id] = s
            except Exception as e:
                print(f"[WARN] Error reading suppliers.json: {e}")
        else:
            for d in get_sample_suppliers():
                s = Supplier.from_dict(d)
                self.suppliers[s.supplier_id] = s

        # Load Prescriptions
        rx_file = self._file_path("prescriptions.json")
        if os.path.exists(rx_file) and os.path.getsize(rx_file) > 2:
            try:
                with open(rx_file, "r", encoding="utf-8") as f:
                    for d in json.load(f):
                        p = Prescription.from_dict(d)
                        self.prescriptions[p.prescription_id] = p
            except Exception as e:
                print(f"[WARN] Error reading prescriptions.json: {e}")
        else:
            for d in get_sample_prescriptions():
                p = Prescription.from_dict(d)
                self.prescriptions[p.prescription_id] = p

        # Load Sales
        sales_file = self._file_path("sales.json")
        if os.path.exists(sales_file) and os.path.getsize(sales_file) > 2:
            try:
                with open(sales_file, "r", encoding="utf-8") as f:
                    for d in json.load(f):
                        self.sales.append(Sale.from_dict(d))
            except Exception as e:
                print(f"[WARN] Error reading sales.json: {e}")

        # Load Bills
        bills_file = self._file_path("bills.json")
        if os.path.exists(bills_file) and os.path.getsize(bills_file) > 2:
            try:
                with open(bills_file, "r", encoding="utf-8") as f:
                    for d in json.load(f):
                        b = Bill.from_dict(d)
                        self.bills[b.bill_id] = b
            except Exception as e:
                print(f"[WARN] Error reading bills.json: {e}")

        # If files were newly created with sample data, save now
        if not os.path.exists(med_file):
            self.save_data()

    # -------------------------------------------------------------
    # MEDICINE & INVENTORY OPERATIONS
    # -------------------------------------------------------------
    @log_action("Add Medicine")
    def add_medicine(self, data: Dict[str, Any]) -> Medicine:
        name = str(data.get("name", "")).strip()
        if not name:
            raise ValueError("Medicine name is required.")

        med_id = data.get("medicine_id") or f"MED-{uuid.uuid4().hex[:6].upper()}"
        if med_id in self.medicines:
            raise ValueError(f"Medicine with ID '{med_id}' already exists.")

        med = Medicine(
            medicine_id=med_id,
            name=name,
            company=str(data.get("company", "Generic")).strip(),
            category=str(data.get("category", "General")).strip(),
            price=float(data.get("price", 0.0)),
            quantity=int(data.get("quantity", 0)),
            expiry_date=str(data.get("expiry_date", datetime.date.today().strftime("%Y-%m-%d"))).strip(),
            batch_no=str(data.get("batch_no", "")).strip(),
            reorder_level=int(data.get("reorder_level", 15)),
            requires_prescription=bool(data.get("requires_prescription", False))
        )
        self.medicines[med.medicine_id] = med
        self.inventory.add_medicine(med)
        self.save_data()
        return med

    def update_medicine(self, med_id: str, data: Dict[str, Any]) -> Medicine:
        med = self.medicines.get(med_id)
        if not med:
            raise MedicineNotFoundError(f"Medicine with ID '{med_id}' not found.")

        if "name" in data and data["name"]:
            med.name = str(data["name"]).strip()
        if "company" in data:
            med.company = str(data["company"]).strip()
        if "category" in data:
            med.category = str(data["category"]).strip()
        if "price" in data:
            med.price = float(data["price"])
        if "quantity" in data:
            med.quantity = int(data["quantity"])
        if "expiry_date" in data and data["expiry_date"]:
            med.expiry_date = str(data["expiry_date"]).strip()
        if "batch_no" in data:
            med.batch_no = str(data["batch_no"]).strip()
        if "reorder_level" in data:
            med.reorder_level = int(data["reorder_level"])
        if "requires_prescription" in data:
            med.requires_prescription = bool(data["requires_prescription"])

        self.save_data()
        return med

    def delete_medicine(self, med_id: str) -> bool:
        if med_id not in self.medicines:
            raise MedicineNotFoundError(f"Medicine with ID '{med_id}' not found.")
        del self.medicines[med_id]
        self.inventory.remove_medicine(med_id)
        self.save_data()
        return True

    def adjust_stock(self, med_id: str, quantity_delta: int) -> Medicine:
        med = self.medicines.get(med_id)
        if not med:
            raise MedicineNotFoundError(f"Medicine '{med_id}' not found.")
        med.update_stock(quantity_delta)
        self.save_data()
        return med

    def get_inventory_alerts(self) -> Dict[str, Any]:
        """Provides lists of low stock and expired/expiring items."""
        low_stock = [m.to_dict() for m in self.inventory.check_low_stock()]
        expired = [m.to_dict() for m in self.inventory.check_expired_medicines()]
        expiring_soon = [m.to_dict() for m in self.inventory.check_expiring_soon(30)]
        return {
            "low_stock_count": len(low_stock),
            "low_stock": low_stock,
            "expired_count": len(expired),
            "expired": expired,
            "expiring_soon_count": len(expiring_soon),
            "expiring_soon": expiring_soon
        }

    # -------------------------------------------------------------
    # CUSTOMER OPERATIONS
    # -------------------------------------------------------------
    def add_customer(self, data: Dict[str, Any]) -> Customer:
        cid = data.get("customer_id") or f"CUST-{uuid.uuid4().hex[:6].upper()}"
        if cid in self.customers:
            raise ValueError(f"Customer with ID '{cid}' already exists.")

        cust = Customer(
            customer_id=cid,
            name=str(data.get("name", "")).strip(),
            mobile_number=str(data.get("mobile", data.get("mobile_number", ""))).strip(),
            address=str(data.get("address", "")).strip()
        )
        self.customers[cust.customer_id] = cust
        self.save_data()
        return cust

    def update_customer(self, cid: str, data: Dict[str, Any]) -> Customer:
        cust = self.customers.get(cid)
        if not cust:
            raise InvalidCustomerError(f"Customer '{cid}' not found.")
        cust.update_details(
            name=data.get("name"),
            mobile=data.get("mobile", data.get("mobile_number")),
            address=data.get("address")
        )
        self.save_data()
        return cust

    def delete_customer(self, cid: str) -> bool:
        if cid not in self.customers:
            raise InvalidCustomerError(f"Customer '{cid}' not found.")
        del self.customers[cid]
        self.save_data()
        return True

    # -------------------------------------------------------------
    # SUPPLIER OPERATIONS
    # -------------------------------------------------------------
    def add_supplier(self, data: Dict[str, Any]) -> Supplier:
        sid = data.get("supplier_id") or f"SUP-{uuid.uuid4().hex[:6].upper()}"
        if sid in self.suppliers:
            raise ValueError(f"Supplier with ID '{sid}' already exists.")

        sup = Supplier(
            supplier_id=sid,
            name=str(data.get("name", "")).strip(),
            mobile_number=str(data.get("mobile", data.get("mobile_number", ""))).strip(),
            address=str(data.get("address", "")).strip(),
            company=str(data.get("company", "")).strip(),
            supplied_medicines=data.get("supplied_medicines", [])
        )
        self.suppliers[sup.supplier_id] = sup
        self.save_data()
        return sup

    def update_supplier(self, sid: str, data: Dict[str, Any]) -> Supplier:
        sup = self.suppliers.get(sid)
        if not sup:
            raise InvalidSupplierError(f"Supplier '{sid}' not found.")
        sup.update_details(
            name=data.get("name"),
            mobile=data.get("mobile", data.get("mobile_number")),
            address=data.get("address")
        )
        if "company" in data:
            sup.company = str(data["company"]).strip()
        if "supplied_medicines" in data:
            sup.supplied_medicines = data["supplied_medicines"]
        self.save_data()
        return sup

    def delete_supplier(self, sid: str) -> bool:
        if sid not in self.suppliers:
            raise InvalidSupplierError(f"Supplier '{sid}' not found.")
        del self.suppliers[sid]
        self.save_data()
        return True

    # -------------------------------------------------------------
    # PRESCRIPTION OPERATIONS
    # -------------------------------------------------------------
    def add_prescription(self, data: Dict[str, Any]) -> Prescription:
        pid = data.get("prescription_id") or f"RX-{uuid.uuid4().hex[:6].upper()}"
        meds = data.get("prescribed_medicines", [])
        if isinstance(meds, str):
            meds = [x.strip() for x in meds.split(",") if x.strip()]

        rx = Prescription(
            prescription_id=pid,
            doctor_name=str(data.get("doctor_name", "Dr. Doctor")).strip(),
            patient_name=str(data.get("patient_name", "Patient")).strip(),
            prescribed_medicines=meds,
            verified=bool(data.get("verified", True)),
            date_issued=data.get("date_issued")
        )
        self.prescriptions[rx.prescription_id] = rx
        self.save_data()
        return rx

    def verify_prescription(self, pid: str) -> Prescription:
        rx = self.prescriptions.get(pid)
        if not rx:
            raise InvalidPrescriptionError(f"Prescription '{pid}' not found.")
        rx.verify_prescription()
        self.save_data()
        return rx

    def delete_prescription(self, pid: str) -> bool:
        if pid not in self.prescriptions:
            raise InvalidPrescriptionError(f"Prescription '{pid}' not found.")
        del self.prescriptions[pid]
        self.save_data()
        return True

    # -------------------------------------------------------------
    # SALES & BILLING OPERATIONS (Core Transaction)
    # -------------------------------------------------------------
    @log_action("Process Sale & Billing")
    def process_sale(self, customer_id: str, items: List[Dict[str, Any]],
                     prescription_id: Optional[str] = None,
                     gst_rate: float = 0.18, discount: float = 0.0,
                     payment_method: str = "Cash") -> Dict[str, Any]:
        """
        Processes a multi-item sale atomically:
        - Validates items, quantities, expiry, and stock
        - Deducts stock from inventory
        - Creates and links Sale and Bill records
        - Appends to customer purchase history
        - Persists data to JSON
        """
        if not items:
            raise InvalidQuantityError("Cannot process sale: items list is empty.")

        # Resolve Customer
        customer = self.customers.get(customer_id)
        if customer:
            c_name = customer.name
            c_id = customer.customer_id
        else:
            c_id = customer_id or "WALKIN"
            c_name = "Walk-in Customer"

        # Validate prescription if required
        rx = self.prescriptions.get(prescription_id) if prescription_id else None

        prepared_items = []
        for it in items:
            med_id = str(it.get("medicine_id", "")).strip()
            qty = int(it.get("quantity", 0))

            if qty <= 0:
                raise InvalidQuantityError(f"Invalid quantity {qty} requested for medicine '{med_id}'.")

            med = self.medicines.get(med_id)
            if not med:
                raise MedicineNotFoundError(f"Medicine ID '{med_id}' not found.")

            # Expiry Check
            med.check_expiry()

            # Prescription Check
            if med.requires_prescription and not rx:
                raise InvalidPrescriptionError(
                    f"Medicine '{med.name}' requires a valid doctor's prescription."
                )

            # Stock check
            if med.quantity < qty:
                raise OutOfStockError(
                    f"Insufficient stock for '{med.name}'. Available: {med.quantity}, Requested: {qty}"
                )

            line_total = round(med.price * qty, 2)
            prepared_items.append({
                "medicine_id": med.medicine_id,
                "name": med.name,
                "company": med.company,
                "category": med.category,
                "unit_price": med.price,
                "quantity": qty,
                "line_total": line_total
            })

        # Atomic stock deduction
        for it in prepared_items:
            med = self.medicines[it["medicine_id"]]
            med.update_stock(-it["quantity"])

        subtotal = round(sum(it["line_total"] for it in prepared_items), 2)
        gst_amount = Bill.calculate_gst(subtotal, gst_rate)
        total_amount = round(subtotal + gst_amount - discount, 2)

        sale_id = f"SALE-{uuid.uuid4().hex[:6].upper()}"
        sale = Sale(
            sale_id=sale_id,
            customer_id=c_id,
            customer_name=c_name,
            items=prepared_items,
            subtotal=subtotal,
            gst=gst_amount,
            total=total_amount,
            prescription_id=prescription_id
        )
        self.sales.append(sale)

        bill_id = f"BILL-{uuid.uuid4().hex[:6].upper()}"
        bill = Bill(
            bill_id=bill_id,
            sale_id=sale_id,
            customer_name=c_name,
            customer_id=c_id,
            items=prepared_items,
            subtotal=subtotal,
            gst_rate=gst_rate,
            discount=discount,
            payment_method=payment_method
        )
        self.bills[bill.bill_id] = bill

        # Record in customer's purchase history if registered
        if customer:
            customer.buy_medicine(sale.to_dict())

        self.save_data()

        return {
            "sale": sale.to_dict(),
            "bill": bill.to_dict()
        }

    # -------------------------------------------------------------
    # DASHBOARD & REPORTS
    # -------------------------------------------------------------
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Provides real-time aggregated metrics for the frontend dashboard."""
        total_revenue = sum(b.total_amount for b in self.bills.values())
        low_stock_count = len(self.inventory.check_low_stock())
        expired_count = len(self.inventory.check_expired_medicines())
        expiring_soon_count = len(self.inventory.check_expiring_soon(30))

        # Recent 5 sales
        recent_sales = [s.to_dict() for s in reversed(self.sales[-5:])]

        return {
            "medicines": len(self.medicines),
            "customers": len(self.customers),
            "suppliers": len(self.suppliers),
            "prescriptions": len(self.prescriptions),
            "sales": len(self.sales),
            "bills": len(self.bills),
            "revenue": round(total_revenue, 2),
            "low_stock_count": low_stock_count,
            "expired_count": expired_count,
            "expiring_soon_count": expiring_soon_count,
            "recent_sales": recent_sales
        }

    def get_sales_report(self) -> List[Dict[str, Any]]:
        """Returns all formatted sales using generator."""
        return list(sales_report_generator(self.sales))

    def export_csv_data(self, resource_type: str) -> str:
        """Generates raw CSV string for specified resource."""
        res = resource_type.lower()
        if res == "medicines":
            rows = [m.to_dict() for m in self.medicines.values()]
        elif res == "customers":
            rows = [c.to_dict() for c in self.customers.values()]
        elif res == "suppliers":
            rows = [s.to_dict() for s in self.suppliers.values()]
        elif res == "prescriptions":
            rows = [p.to_dict() for p in self.prescriptions.values()]
        elif res == "sales":
            rows = self.get_sales_report()
        elif res == "bills":
            rows = [b.to_dict() for b in self.bills.values()]
        else:
            raise ValueError(f"Unknown resource type for CSV export: '{resource_type}'")

        return export_to_csv_string(rows)
