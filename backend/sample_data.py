"""
Realistic sample data generator for initial store bootstrap.
"""

import datetime


def get_sample_medicines():
    today = datetime.date.today()
    return [
        {
            "medicine_id": "MED-101",
            "name": "Paracetamol 650mg",
            "company": "Cipla Ltd.",
            "category": "Antipyretic / Analgesic",
            "price": 32.50,
            "quantity": 120,
            "expiry_date": (today + datetime.timedelta(days=365)).strftime("%Y-%m-%d"),
            "batch_no": "B-PCM650",
            "reorder_level": 25,
            "requires_prescription": False
        },
        {
            "medicine_id": "MED-102",
            "name": "Amoxicillin 500mg",
            "company": "Sun Pharma",
            "category": "Antibiotic",
            "price": 85.00,
            "quantity": 45,
            "expiry_date": (today + datetime.timedelta(days=240)).strftime("%Y-%m-%d"),
            "batch_no": "B-AMX500",
            "reorder_level": 20,
            "requires_prescription": True
        },
        {
            "medicine_id": "MED-103",
            "name": "Cetirizine 10mg",
            "company": "Dr. Reddy's",
            "category": "Antihistamine",
            "price": 18.00,
            "quantity": 90,
            "expiry_date": (today + datetime.timedelta(days=500)).strftime("%Y-%m-%d"),
            "batch_no": "B-CET10",
            "reorder_level": 15,
            "requires_prescription": False
        },
        {
            "medicine_id": "MED-104",
            "name": "Metformin 500mg",
            "company": "Torrent Pharma",
            "category": "Antidiabetic",
            "price": 42.00,
            "quantity": 8,  # Low stock test
            "expiry_date": (today + datetime.timedelta(days=400)).strftime("%Y-%m-%d"),
            "batch_no": "B-MET500",
            "reorder_level": 15,
            "requires_prescription": True
        },
        {
            "medicine_id": "MED-105",
            "name": "Azithromycin 500mg",
            "company": "Lupin Ltd.",
            "category": "Antibiotic",
            "price": 115.00,
            "quantity": 30,
            "expiry_date": (today + datetime.timedelta(days=180)).strftime("%Y-%m-%d"),
            "batch_no": "B-AZI500",
            "reorder_level": 10,
            "requires_prescription": True
        },
        {
            "medicine_id": "MED-106",
            "name": "Omeprazole 20mg",
            "company": "Alkem Labs",
            "category": "Antacid / PPI",
            "price": 55.00,
            "quantity": 60,
            "expiry_date": (today + datetime.timedelta(days=300)).strftime("%Y-%m-%d"),
            "batch_no": "B-OMP20",
            "reorder_level": 20,
            "requires_prescription": False
        },
        {
            "medicine_id": "MED-107",
            "name": "Ibuprofen 400mg",
            "company": "Abbott",
            "category": "NSAID / Pain Relief",
            "price": 28.00,
            "quantity": 5,  # Low stock test
            "expiry_date": (today + datetime.timedelta(days=600)).strftime("%Y-%m-%d"),
            "batch_no": "B-IBU400",
            "reorder_level": 15,
            "requires_prescription": False
        },
        {
            "medicine_id": "MED-108",
            "name": "Cough Syrup Dextro 100ml",
            "company": "Dabur Pharma",
            "category": "Cough & Cold",
            "price": 95.00,
            "quantity": 25,
            "expiry_date": (today - datetime.timedelta(days=15)).strftime("%Y-%m-%d"),  # Expired test
            "batch_no": "B-CGH100",
            "reorder_level": 10,
            "requires_prescription": False
        },
        {
            "medicine_id": "MED-109",
            "name": "Vitamin D3 60K IU",
            "company": "Cadila Health",
            "category": "Supplements",
            "price": 120.00,
            "quantity": 50,
            "expiry_date": (today + datetime.timedelta(days=15)).strftime("%Y-%m-%d"),  # Expiring soon test
            "batch_no": "B-VITD3",
            "reorder_level": 10,
            "requires_prescription": False
        }
    ]


def get_sample_customers():
    return [
        {
            "customer_id": "CUST-001",
            "name": "Rahul Sharma",
            "mobile": "+91 98765 43210",
            "address": "45 Park Street, Sector 14, Delhi",
            "purchase_history": []
        },
        {
            "customer_id": "CUST-002",
            "name": "Priya Nair",
            "mobile": "+91 91234 56789",
            "address": "12 Richmond Town, Bengaluru",
            "purchase_history": []
        },
        {
            "customer_id": "CUST-003",
            "name": "Amitabh Sen",
            "mobile": "+91 99887 76655",
            "address": "78 Salt Lake City, Kolkata",
            "purchase_history": []
        }
    ]


def get_sample_suppliers():
    return [
        {
            "supplier_id": "SUP-101",
            "name": "Apex Pharma Distributors",
            "mobile": "+91 98111 22334",
            "address": "Warehouse 4B, Industrial Estate, Mumbai",
            "company": "Apex Healthcare Logistics",
            "supplied_medicines": ["MED-101", "MED-102", "MED-105"]
        },
        {
            "supplier_id": "SUP-102",
            "name": "MediLife Supply Corp",
            "mobile": "+91 98222 33445",
            "address": "Plot 12, GIDC Pharma Hub, Ahmedabad",
            "company": "MediLife Global",
            "supplied_medicines": ["MED-103", "MED-104", "MED-106", "MED-107"]
        }
    ]


def get_sample_prescriptions():
    today = datetime.date.today().strftime("%Y-%m-%d")
    return [
        {
            "prescription_id": "RX-501",
            "doctor_name": "Dr. A. K. Verma (MD General)",
            "patient_name": "Rahul Sharma",
            "prescribed_medicines": ["Amoxicillin 500mg", "Paracetamol 650mg"],
            "verified": True,
            "date_issued": today
        },
        {
            "prescription_id": "RX-502",
            "doctor_name": "Dr. Sneha Roy (Endocrinologist)",
            "patient_name": "Amitabh Sen",
            "prescribed_medicines": ["Metformin 500mg"],
            "verified": True,
            "date_issued": today
        }
    ]
