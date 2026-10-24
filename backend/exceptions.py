"""
Custom Exception Classes for Medicine Store Management System.
Provides distinct error types for business logic, inventory, validation, and billing.
"""

class MedicineStoreError(Exception):
    """Base exception for all domain errors in the medicine store system."""
    def __init__(self, message: str, code: str = "STORE_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

    def to_dict(self):
        return {"error": self.message, "code": self.code}


class MedicineNotFoundError(MedicineStoreError):
    def __init__(self, message: str = "Medicine not found."):
        super().__init__(message, code="MEDICINE_NOT_FOUND", status_code=404)


class OutOfStockError(MedicineStoreError):
    def __init__(self, message: str = "Insufficient stock available."):
        super().__init__(message, code="OUT_OF_STOCK", status_code=400)


class ExpiredMedicineError(MedicineStoreError):
    def __init__(self, message: str = "Medicine is expired and cannot be sold."):
        super().__init__(message, code="EXPIRED_MEDICINE", status_code=400)


class InvalidCustomerError(MedicineStoreError):
    def __init__(self, message: str = "Customer not found or invalid."):
        super().__init__(message, code="INVALID_CUSTOMER", status_code=404)


class InvalidSupplierError(MedicineStoreError):
    def __init__(self, message: str = "Supplier not found or invalid."):
        super().__init__(message, code="INVALID_SUPPLIER", status_code=404)


class InvalidQuantityError(MedicineStoreError):
    def __init__(self, message: str = "Quantity must be a positive integer."):
        super().__init__(message, code="INVALID_QUANTITY", status_code=400)


class InvalidPrescriptionError(MedicineStoreError):
    def __init__(self, message: str = "Prescription is invalid or missing."):
        super().__init__(message, code="INVALID_PRESCRIPTION", status_code=400)
