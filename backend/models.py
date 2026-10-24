"""
Object-Oriented Data Models for Medicine Store Management System.
Implements:
- Abstract Base Class: Person
- Inherited Subclasses: Customer, Supplier
- Core Models: Medicine, Inventory, Prescription, Sale, Bill, Report
- Encapsulation, Polymorphism, and Type Safety
"""

from abc import ABC, abstractmethod
import datetime
import uuid
from typing import List, Dict, Any, Optional
from backend.exceptions import (
    ExpiredMedicineError,
    OutOfStockError,
    InvalidQuantityError
)


class Person(ABC):
    """
    Abstract Base Class for individuals in the system (Customer, Supplier).
    Demonstrates OOP Encapsulation and Abstraction.
    """
    def __init__(self, person_id: str, name: str, mobile_number: str, address: str):
        self._person_id = str(person_id).strip()
        self._name = str(name).strip()
        self._mobile_number = str(mobile_number).strip()
        self._address = str(address).strip()

    @property
    def person_id(self) -> str:
        return self._person_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        if not val or not str(val).strip():
            raise ValueError("Name cannot be empty.")
        self._name = str(val).strip()

    @property
    def mobile_number(self) -> str:
        return self._mobile_number

    @mobile_number.setter
    def mobile_number(self, val: str):
        self._mobile_number = str(val).strip()

    @property
    def address(self) -> str:
        return self._address

    @address.setter
    def address(self, val: str):
        self._address = str(val).strip()

    @abstractmethod
    def display_details(self) -> str:
        """Abstract method implemented polymorphically by subclasses."""
        pass

    def update_details(self, name: Optional[str] = None, mobile: Optional[str] = None, address: Optional[str] = None):
        if name:
            self.name = name
        if mobile:
            self.mobile_number = mobile
        if address:
            self.address = address

    def __str__(self) -> str:
        return f"Person[{self._person_id}]: {self._name} ({self._mobile_number})"


class Customer(Person):
    """
    Customer entity inheriting from Person.
    Manages purchase histories and customer-specific transactions.
    """
    def __init__(self, customer_id: str, name: str, mobile_number: str, address: str,
                 purchase_history: Optional[List[Dict[str, Any]]] = None):
        super().__init__(customer_id, name, mobile_number, address)
        self.customer_id = self._person_id
        self.purchase_history: List[Dict[str, Any]] = purchase_history or []

    def display_details(self) -> str:
        return f"Customer #{self.customer_id} | Name: {self._name} | Mobile: {self._mobile_number} | Purchases: {len(self.purchase_history)}"

    def buy_medicine(self, sale_record: Dict[str, Any]):
        """Records a new purchase to this customer's history."""
        self.purchase_history.append(sale_record)

    def view_purchase_history(self) -> List[Dict[str, Any]]:
        return self.purchase_history

    def to_dict(self) -> Dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "name": self._name,
            "mobile": self._mobile_number,
            "address": self._address,
            "purchase_count": len(self.purchase_history),
            "purchase_history": self.purchase_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Customer":
        cid = data.get("customer_id") or data.get("id") or str(uuid.uuid4())[:8]
        return cls(
            customer_id=cid,
            name=data.get("name", ""),
            mobile_number=data.get("mobile", data.get("mobile_number", "")),
            address=data.get("address", ""),
            purchase_history=data.get("purchase_history", [])
        )


class Supplier(Person):
    """
    Supplier entity inheriting from Person.
    Tracks company associations and medicines supplied.
    """
    def __init__(self, supplier_id: str, name: str, mobile_number: str, address: str,
                 company: str = "", supplied_medicines: Optional[List[str]] = None):
        super().__init__(supplier_id, name, mobile_number, address)
        self.supplier_id = self._person_id
        self.company = company
        self.supplied_medicines: List[str] = supplied_medicines or []

    def display_details(self) -> str:
        return f"Supplier #{self.supplier_id} | Name: {self._name} | Company: {self.company} | Mobile: {self._mobile_number}"

    def supply_medicine(self, medicine_name_or_id: str):
        if medicine_name_or_id not in self.supplied_medicines:
            self.supplied_medicines.append(medicine_name_or_id)

    def view_supply_details(self) -> List[str]:
        return self.supplied_medicines

    def to_dict(self) -> Dict[str, Any]:
        return {
            "supplier_id": self.supplier_id,
            "name": self._name,
            "mobile": self._mobile_number,
            "address": self._address,
            "company": self.company,
            "supplied_medicines": self.supplied_medicines
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Supplier":
        sid = data.get("supplier_id") or data.get("id") or str(uuid.uuid4())[:8]
        return cls(
            supplier_id=sid,
            name=data.get("name", ""),
            mobile_number=data.get("mobile", data.get("mobile_number", "")),
            address=data.get("address", ""),
            company=data.get("company", ""),
            supplied_medicines=data.get("supplied_medicines", [])
        )


class Medicine:
    """
    Medicine entity encapsulating pharmaceutical stock details, pricing,
    expiry date evaluation, and batch tracking.
    """
    def __init__(self, medicine_id: str, name: str, company: str, category: str,
                 price: float, quantity: int, expiry_date: str, batch_no: str = "",
                 reorder_level: int = 15, requires_prescription: bool = False):
        self.medicine_id = str(medicine_id).strip()
        self.name = str(name).strip()
        self.company = str(company).strip()
        self.category = str(category).strip()
        self.price = float(price)
        self.quantity = int(quantity)
        self.expiry_date = str(expiry_date).strip()  # Format: "YYYY-MM-DD"
        self.batch_no = str(batch_no).strip() or f"B-{uuid.uuid4().hex[:6].upper()}"
        self.reorder_level = int(reorder_level)
        self.requires_prescription = bool(requires_prescription)

    def is_expired(self) -> bool:
        """Returns True if the medicine's expiry date is strictly in the past."""
        try:
            exp = datetime.datetime.strptime(self.expiry_date, "%Y-%m-%d").date()
            return exp < datetime.date.today()
        except Exception:
            return False

    def days_until_expiry(self) -> int:
        """Calculates days remaining before expiration."""
        try:
            exp = datetime.datetime.strptime(self.expiry_date, "%Y-%m-%d").date()
            return (exp - datetime.date.today()).days
        except Exception:
            return 9999

    def check_expiry(self) -> bool:
        """Validates expiration; raises ExpiredMedicineError if expired."""
        if self.is_expired():
            raise ExpiredMedicineError(f"Medicine '{self.name}' [ID: {self.medicine_id}] expired on {self.expiry_date}!")
        return True

    def update_stock(self, delta_qty: int):
        """Updates stock quantity; validates sufficient quantity for deduction."""
        delta = int(delta_qty)
        if delta < 0 and abs(delta) > self.quantity:
            raise OutOfStockError(
                f"Insufficient stock for '{self.name}'. Available: {self.quantity}, Requested: {abs(delta)}"
            )
        self.quantity += delta

    def display_medicine(self) -> str:
        return (f"[{self.medicine_id}] {self.name} ({self.category}) - ₹{self.price:.2f} | "
                f"Qty: {self.quantity} | Exp: {self.expiry_date}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "medicine_id": self.medicine_id,
            "name": self.name,
            "company": self.company,
            "category": self.category,
            "price": round(self.price, 2),
            "quantity": self.quantity,
            "expiry_date": self.expiry_date,
            "batch_no": self.batch_no,
            "reorder_level": self.reorder_level,
            "requires_prescription": self.requires_prescription,
            "is_expired": self.is_expired(),
            "days_left": self.days_until_expiry()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Medicine":
        mid = data.get("medicine_id") or data.get("id") or f"MED-{uuid.uuid4().hex[:6].upper()}"
        return cls(
            medicine_id=mid,
            name=data.get("name", "Unknown Medicine"),
            company=data.get("company", "Generic"),
            category=data.get("category", "General"),
            price=float(data.get("price", 0.0)),
            quantity=int(data.get("quantity", 0)),
            expiry_date=data.get("expiry_date", datetime.date.today().strftime("%Y-%m-%d")),
            batch_no=data.get("batch_no", ""),
            reorder_level=int(data.get("reorder_level", 15)),
            requires_prescription=bool(data.get("requires_prescription", False))
        )


class Inventory:
    """
    Inventory class managing collections of Medicines, stock entries,
    and automatic alert queries (low stock, expiring soon).
    """
    def __init__(self, inventory_id: str = "INV-01"):
        self.inventory_id = inventory_id
        self.medicines: Dict[str, Medicine] = {}

    def add_medicine(self, med: Medicine):
        self.medicines[med.medicine_id] = med

    def remove_medicine(self, med_id: str) -> Optional[Medicine]:
        return self.medicines.pop(med_id, None)

    def get_medicine(self, med_id: str) -> Optional[Medicine]:
        return self.medicines.get(med_id)

    def add_stock(self, med_id: str, qty: int):
        med = self.get_medicine(med_id)
        if not med:
            raise ValueError(f"Medicine ID '{med_id}' not found in inventory.")
        med.update_stock(qty)

    def remove_stock(self, med_id: str, qty: int):
        med = self.get_medicine(med_id)
        if not med:
            raise ValueError(f"Medicine ID '{med_id}' not found in inventory.")
        med.update_stock(-qty)

    def check_low_stock(self) -> List[Medicine]:
        """Returns list of medicines whose stock is at or below reorder level."""
        return [m for m in self.medicines.values() if m.quantity <= m.reorder_level]

    def check_expired_medicines(self) -> List[Medicine]:
        """Returns medicines that are past expiration."""
        return [m for m in self.medicines.values() if m.is_expired()]

    def check_expiring_soon(self, days: int = 30) -> List[Medicine]:
        """Returns medicines expiring within given days and not yet expired."""
        return [m for m in self.medicines.values() if 0 <= m.days_until_expiry() <= days]

    def view_inventory(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self.medicines.values()]


class Prescription:
    """
    Prescription entity storing doctor authorization, patient name,
    and required medicines list.
    """
    def __init__(self, prescription_id: str, doctor_name: str, patient_name: str,
                 prescribed_medicines: List[str], verified: bool = True,
                 date_issued: Optional[str] = None):
        self.prescription_id = str(prescription_id).strip()
        self.doctor_name = str(doctor_name).strip()
        self.patient_name = str(patient_name).strip()
        self.prescribed_medicines = [str(m).strip() for m in prescribed_medicines if str(m).strip()]
        self.verified = bool(verified)
        self.date_issued = date_issued or datetime.date.today().strftime("%Y-%m-%d")

    def verify_prescription(self) -> bool:
        self.verified = True
        return self.verified

    def display_prescription(self) -> str:
        status = "Verified" if self.verified else "Unverified"
        meds = ", ".join(self.prescribed_medicines)
        return f"Rx #{self.prescription_id} | Dr. {self.doctor_name} -> {self.patient_name} [{status}] Meds: {meds}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prescription_id": self.prescription_id,
            "doctor_name": self.doctor_name,
            "patient_name": self.patient_name,
            "prescribed_medicines": self.prescribed_medicines,
            "verified": self.verified,
            "date_issued": self.date_issued
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Prescription":
        pid = data.get("prescription_id") or data.get("id") or f"RX-{uuid.uuid4().hex[:6].upper()}"
        meds = data.get("prescribed_medicines", [])
        if isinstance(meds, str):
            meds = [x.strip() for x in meds.split(",") if x.strip()]
        return cls(
            prescription_id=pid,
            doctor_name=data.get("doctor_name", "Dr. Unknown"),
            patient_name=data.get("patient_name", "Patient"),
            prescribed_medicines=meds,
            verified=bool(data.get("verified", True)),
            date_issued=data.get("date_issued", datetime.date.today().strftime("%Y-%m-%d"))
        )


class Sale:
    """
    Represents a finalized medicine sale transaction containing multiple line items.
    """
    def __init__(self, sale_id: str, customer_id: str, customer_name: str,
                 items: List[Dict[str, Any]], subtotal: float = 0.0,
                 gst: float = 0.0, total: float = 0.0,
                 sale_date: Optional[str] = None, prescription_id: Optional[str] = None):
        self.sale_id = str(sale_id).strip()
        self.customer_id = str(customer_id).strip()
        self.customer_name = str(customer_name).strip()
        self.items = items  # [{medicine_id, name, unit_price, quantity, line_total}]
        self.subtotal = float(subtotal)
        self.gst = float(gst)
        self.total = float(total)
        self.sale_date = sale_date or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.prescription_id = prescription_id

    def calculate_total(self) -> float:
        self.subtotal = sum(float(item.get("line_total", 0.0)) for item in self.items)
        self.total = round(self.subtotal + self.gst, 2)
        return self.total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sale_id": self.sale_id,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "items": self.items,
            "subtotal": round(self.subtotal, 2),
            "gst": round(self.gst, 2),
            "total": round(self.total, 2),
            "sale_date": self.sale_date,
            "prescription_id": self.prescription_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Sale":
        sid = data.get("sale_id") or f"SALE-{uuid.uuid4().hex[:6].upper()}"
        return cls(
            sale_id=sid,
            customer_id=data.get("customer_id", "WALKIN"),
            customer_name=data.get("customer_name", "Walk-in Customer"),
            items=data.get("items", []),
            subtotal=float(data.get("subtotal", 0.0)),
            gst=float(data.get("gst", 0.0)),
            total=float(data.get("total", 0.0)),
            sale_date=data.get("sale_date"),
            prescription_id=data.get("prescription_id")
        )


class Bill:
    """
    Bill entity for tax calculations, invoice generation, and receipt printing.
    """
    GST_SLABS = (0.00, 0.05, 0.12, 0.18)  # Available GST slabs

    def __init__(self, bill_id: str, sale_id: str, customer_name: str,
                 customer_id: str, items: List[Dict[str, Any]],
                 subtotal: float, gst_rate: float = 0.18, discount: float = 0.0,
                 bill_date: Optional[str] = None, payment_method: str = "Cash"):
        self.bill_id = str(bill_id).strip()
        self.sale_id = str(sale_id).strip()
        self.customer_name = str(customer_name).strip()
        self.customer_id = str(customer_id).strip()
        self.items = items
        self.subtotal = float(subtotal)
        self.gst_rate = float(gst_rate)
        self.discount = float(discount)
        self.bill_date = bill_date or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.payment_method = payment_method

        self.gst_amount = self.calculate_gst(self.subtotal, self.gst_rate)
        self.total_amount = round(self.subtotal + self.gst_amount - self.discount, 2)

    @staticmethod
    def calculate_gst(amount: float, rate: float = 0.18) -> float:
        """Static method calculating GST tax amount."""
        return round(float(amount) * float(rate), 2)

    def generate_bill(self) -> Dict[str, Any]:
        """Calculates final amounts and returns dictionary format."""
        self.gst_amount = self.calculate_gst(self.subtotal, self.gst_rate)
        self.total_amount = round(self.subtotal + self.gst_amount - self.discount, 2)
        return self.to_dict()

    def print_bill(self) -> str:
        """Generates an ASCII receipt representation (console-safe)."""
        lines = [
            "=" * 48,
            "       PHARMA-MS MEDICINE STORE RECEIPT       ",
            "=" * 48,
            f"Bill ID : {self.bill_id}   Date: {self.bill_date}",
            f"Customer: {self.customer_name} (ID: {self.customer_id})",
            f"Payment : {self.payment_method}",
            "-" * 48,
            f"{'Item Name':<22}{'Qty':<6}{'Rate':<9}{'Total':<10}",
            "-" * 48
        ]
        for it in self.items:
            name = it.get("name", "Item")[:20]
            qty = it.get("quantity", 1)
            rate = it.get("unit_price", 0.0)
            tot = it.get("line_total", 0.0)
            lines.append(f"{name:<22}{qty:<6}{rate:<9.2f}{tot:<10.2f}")

        lines.extend([
            "-" * 48,
            f"{'Subtotal:':<35} Rs.{self.subtotal:.2f}",
            f"{f'GST ({int(self.gst_rate*100)}%):':<35} Rs.{self.gst_amount:.2f}",
            f"{'Discount:':<35} -Rs.{self.discount:.2f}",
            "=" * 48,
            f"{'GRAND TOTAL:':<35} Rs.{self.total_amount:.2f}",
            "=" * 48,
            "     Thank you for your visit! Get well soon!   ",
            "=" * 48
        ])
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bill_id": self.bill_id,
            "sale_id": self.sale_id,
            "customer_name": self.customer_name,
            "customer_id": self.customer_id,
            "items": self.items,
            "subtotal": round(self.subtotal, 2),
            "gst_rate": self.gst_rate,
            "gst": round(self.gst_amount, 2),
            "discount": round(self.discount, 2),
            "total": round(self.total_amount, 2),
            "bill_date": self.bill_date,
            "payment_method": self.payment_method,
            "receipt_text": self.print_bill()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Bill":
        bid = data.get("bill_id") or f"BILL-{uuid.uuid4().hex[:6].upper()}"
        return cls(
            bill_id=bid,
            sale_id=data.get("sale_id", ""),
            customer_name=data.get("customer_name", "Customer"),
            customer_id=data.get("customer_id", ""),
            items=data.get("items", []),
            subtotal=float(data.get("subtotal", 0.0)),
            gst_rate=float(data.get("gst_rate", 0.18)),
            discount=float(data.get("discount", 0.0)),
            bill_date=data.get("bill_date"),
            payment_method=data.get("payment_method", "Cash")
        )


class Report:
    """
    Reporting entity managing daily/monthly sales, stock levels,
    expiry evaluations, and export formatting.
    """
    def __init__(self, report_id: str, report_type: str, data: Any = None):
        self.report_id = report_id
        self.report_type = report_type
        self.generated_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data = data or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type,
            "generated_date": self.generated_date,
            "data": self.data
        }
