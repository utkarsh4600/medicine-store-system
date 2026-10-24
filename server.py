"""
High-Performance Zero-Dependency REST API & Web Server.
Uses Python's standard library `http.server` to serve:
- Modern Frontend SPA (HTML, CSS, JS)
- Complete RESTful JSON APIs for Medicine Store Management System
- CORS Support for Cross-Origin requests
"""

import sys
import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Ensure project root is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.store import MedicineStoreManagementSystem
from backend.exceptions import MedicineStoreError

# Initialize singleton store
store = MedicineStoreManagementSystem()
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


class MedicineStoreHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler routing API calls and serving frontend assets."""

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _send_json(self, data, status_code: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, message: str, status_code: int = 400, code: str = "ERROR"):
        self._send_json({"error": message, "code": code}, status_code=status_code)

    def _send_file(self, filepath: str, content_type: str):
        if not os.path.exists(filepath):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(content)

    def _parse_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length <= 0:
            return {}
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors_headers()
        self.end_headers()

    # -------------------------------------------------------------
    # GET REQUESTS
    # -------------------------------------------------------------
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = urllib.parse.parse_qs(parsed.query)

        # Static Assets
        if path == "" or path == "/index.html":
            return self._send_file(os.path.join(FRONTEND_DIR, "index.html"), "text/html; charset=utf-8")
        elif path == "/styles.css":
            return self._send_file(os.path.join(FRONTEND_DIR, "styles.css"), "text/css; charset=utf-8")
        elif path == "/app.js":
            return self._send_file(os.path.join(FRONTEND_DIR, "app.js"), "application/javascript; charset=utf-8")

        # API Routes
        try:
            if path == "/api/dashboard":
                return self._send_json(store.get_dashboard_summary())

            elif path == "/api/medicines":
                category = query.get("category", [None])[0]
                search = query.get("search", [None])[0]
                status_filter = query.get("status", [None])[0]

                meds = [m.to_dict() for m in store.medicines.values()]
                if category and category.lower() != "all":
                    meds = [m for m in meds if m["category"].lower() == category.lower()]
                if search:
                    q = search.lower()
                    meds = [m for m in meds if q in m["name"].lower() or q in m["medicine_id"].lower() or q in m["company"].lower()]
                if status_filter == "low_stock":
                    meds = [m for m in meds if m["quantity"] <= m["reorder_level"]]
                elif status_filter == "expired":
                    meds = [m for m in meds if m["is_expired"]]

                return self._send_json(meds)

            elif path.startswith("/api/medicines/"):
                med_id = urllib.parse.unquote(path.split("/")[-1])
                med = store.medicines.get(med_id)
                if not med:
                    return self._send_error(f"Medicine '{med_id}' not found", status_code=404)
                return self._send_json(med.to_dict())

            elif path == "/api/customers":
                return self._send_json([c.to_dict() for c in store.customers.values()])

            elif path.startswith("/api/customers/") and path.endswith("/history"):
                cid = urllib.parse.unquote(path.split("/")[-2])
                cust = store.customers.get(cid)
                if not cust:
                    return self._send_error(f"Customer '{cid}' not found", status_code=404)
                return self._send_json(cust.view_purchase_history())

            elif path == "/api/suppliers":
                return self._send_json([s.to_dict() for s in store.suppliers.values()])

            elif path == "/api/prescriptions":
                return self._send_json([p.to_dict() for p in store.prescriptions.values()])

            elif path == "/api/sales":
                return self._send_json([s.to_dict() for s in store.sales])

            elif path == "/api/bills":
                return self._send_json([b.to_dict() for b in store.bills.values()])

            elif path.startswith("/api/bills/"):
                bid = urllib.parse.unquote(path.split("/")[-1])
                bill = store.bills.get(bid)
                if not bill:
                    return self._send_error(f"Bill '{bid}' not found", status_code=404)
                return self._send_json(bill.to_dict())

            elif path == "/api/inventory/alerts":
                return self._send_json(store.get_inventory_alerts())

            elif path.startswith("/api/export/"):
                res_type = path.split("/")[-1]
                csv_data = store.export_csv_data(res_type)
                body = csv_data.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", f"attachment; filename={res_type}.csv")
                self.send_header("Content-Length", str(len(body)))
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(body)
                return

            else:
                return self._send_error(f"Endpoint '{path}' not found", status_code=404)

        except Exception as e:
            return self._send_error(str(e), status_code=500)

    # -------------------------------------------------------------
    # POST REQUESTS
    # -------------------------------------------------------------
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        data = self._parse_body()

        try:
            if path == "/api/medicines":
                med = store.add_medicine(data)
                return self._send_json(med.to_dict(), status_code=201)

            elif path == "/api/customers":
                cust = store.add_customer(data)
                return self._send_json(cust.to_dict(), status_code=201)

            elif path == "/api/suppliers":
                sup = store.add_supplier(data)
                return self._send_json(sup.to_dict(), status_code=201)

            elif path == "/api/prescriptions":
                rx = store.add_prescription(data)
                return self._send_json(rx.to_dict(), status_code=201)

            elif path == "/api/sales":
                cid = data.get("customer_id")
                items = data.get("items", [])
                rx_id = data.get("prescription_id")
                gst_rate = float(data.get("gst_rate", 0.18))
                discount = float(data.get("discount", 0.0))
                payment_method = str(data.get("payment_method", "Cash"))

                result = store.process_sale(
                    customer_id=cid,
                    items=items,
                    prescription_id=rx_id,
                    gst_rate=gst_rate,
                    discount=discount,
                    payment_method=payment_method
                )
                return self._send_json(result, status_code=201)

            elif path.startswith("/api/medicines/") and path.endswith("/stock"):
                med_id = urllib.parse.unquote(path.split("/")[-2])
                delta = int(data.get("quantity", 0))
                med = store.adjust_stock(med_id, delta)
                return self._send_json(med.to_dict())

            elif path == "/api/save":
                store.save_data()
                return self._send_json({"message": "Data saved successfully", "status": "ok"})

            elif path == "/api/reload":
                store.load_data()
                return self._send_json({"message": "Data reloaded successfully", "status": "ok"})

            else:
                return self._send_error(f"Endpoint '{path}' not found", status_code=404)

        except MedicineStoreError as e:
            return self._send_error(e.message, status_code=e.status_code, code=e.code)
        except Exception as e:
            return self._send_error(str(e), status_code=400)

    # -------------------------------------------------------------
    # PUT REQUESTS
    # -------------------------------------------------------------
    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        data = self._parse_body()

        try:
            if path.startswith("/api/medicines/"):
                med_id = urllib.parse.unquote(path.split("/")[-1])
                med = store.update_medicine(med_id, data)
                return self._send_json(med.to_dict())

            elif path.startswith("/api/customers/"):
                cid = urllib.parse.unquote(path.split("/")[-1])
                cust = store.update_customer(cid, data)
                return self._send_json(cust.to_dict())

            elif path.startswith("/api/suppliers/"):
                sid = urllib.parse.unquote(path.split("/")[-1])
                sup = store.update_supplier(sid, data)
                return self._send_json(sup.to_dict())

            elif path.startswith("/api/prescriptions/") and path.endswith("/verify"):
                pid = urllib.parse.unquote(path.split("/")[-2])
                rx = store.verify_prescription(pid)
                return self._send_json(rx.to_dict())

            else:
                return self._send_error(f"Endpoint '{path}' not found", status_code=404)

        except MedicineStoreError as e:
            return self._send_error(e.message, status_code=e.status_code, code=e.code)
        except Exception as e:
            return self._send_error(str(e), status_code=400)

    # -------------------------------------------------------------
    # DELETE REQUESTS
    # -------------------------------------------------------------
    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        try:
            if path.startswith("/api/medicines/"):
                med_id = urllib.parse.unquote(path.split("/")[-1])
                store.delete_medicine(med_id)
                return self._send_json({"message": f"Medicine '{med_id}' deleted."})

            elif path.startswith("/api/customers/"):
                cid = urllib.parse.unquote(path.split("/")[-1])
                store.delete_customer(cid)
                return self._send_json({"message": f"Customer '{cid}' deleted."})

            elif path.startswith("/api/suppliers/"):
                sid = urllib.parse.unquote(path.split("/")[-1])
                store.delete_supplier(sid)
                return self._send_json({"message": f"Supplier '{sid}' deleted."})

            elif path.startswith("/api/prescriptions/"):
                pid = urllib.parse.unquote(path.split("/")[-1])
                store.delete_prescription(pid)
                return self._send_json({"message": f"Prescription '{pid}' deleted."})

            else:
                return self._send_error(f"Endpoint '{path}' not found", status_code=404)

        except MedicineStoreError as e:
            return self._send_error(e.message, status_code=e.status_code, code=e.code)
        except Exception as e:
            return self._send_error(str(e), status_code=400)

    def log_message(self, format, *args):
        # Override standard log to output cleaner lines
        sys.stderr.write(f"[{self.log_date_time_string()}] {args[0]} {args[1]} -> {args[2]}\n")


def run_server(port: int = 8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, MedicineStoreHandler)
    print("=" * 60)
    print(f"  PHARMA-MS MEDICINE STORE SERVER RUNNING")
    print(f"  Local Address: http://localhost:{port}")
    print(f"  API Endpoint:  http://localhost:{port}/api/dashboard")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
        store.save_data()
        httpd.server_close()


if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
