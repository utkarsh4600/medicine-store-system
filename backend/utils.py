"""
Utilities, Decorators, Generators, and Helper Functions.
Includes logging decorators, sales generators, lambda sorting, and CSV serialization.
"""

import functools
import datetime
import csv
import io
import time
from typing import Callable, Any, List, Dict, Generator


def log_action(action_name: str) -> Callable:
    """
    Decorator factory that logs function execution with timestamps.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] [LOG] {action_name} started...")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.time() - start_time) * 1000
                print(f"[{ts}] [LOG] {action_name} completed in {elapsed:.2f}ms.")
                return result
            except Exception as e:
                print(f"[{ts}] [ERROR] {action_name} failed: {e}")
                raise
        return wrapper
    return decorator


def time_execution(func: Callable) -> Callable:
    """Decorator to measure execution duration."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        res = func(*args, **kwargs)
        duration = (time.perf_counter() - start) * 1000
        # attach duration if dictionary
        if isinstance(res, dict):
            res["_execution_ms"] = round(duration, 2)
        return res
    return wrapper


def sales_report_generator(sales_list: List[Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Generator yielding formatted sale records one by one to optimize memory.
    """
    for sale in sales_list:
        sale_data = sale.to_dict() if hasattr(sale, "to_dict") else dict(sale)
        yield {
            "sale_id": sale_data.get("sale_id"),
            "customer_id": sale_data.get("customer_id"),
            "customer_name": sale_data.get("customer_name", "N/A"),
            "item_count": len(sale_data.get("items", [])),
            "subtotal": sale_data.get("subtotal", 0.0),
            "gst": sale_data.get("gst", 0.0),
            "total": sale_data.get("total", 0.0),
            "sale_date": sale_data.get("sale_date")
        }


# Lambda sorting and filtering helpers
sort_by_price = lambda items, reverse=False: sorted(items, key=lambda x: getattr(x, 'price', 0), reverse=reverse)
sort_by_expiry = lambda items, reverse=False: sorted(items, key=lambda x: getattr(x, 'expiry_date', ''), reverse=reverse)
sort_by_name = lambda items: sorted(items, key=lambda x: getattr(x, 'name', '').lower())
filter_low_stock = lambda items, threshold=10: [x for x in items if getattr(x, 'quantity', 0) <= threshold]


def export_to_csv_string(rows: List[Dict[str, Any]], fieldnames: List[str] = None) -> str:
    """Serializes a list of dictionaries to a CSV formatted string."""
    if not rows:
        return ""
    if not fieldnames:
        fieldnames = list(rows[0].keys())

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    for row in rows:
        # Flatten lists/dicts for clean CSV representation
        clean_row = {}
        for k, v in row.items():
            if isinstance(v, (list, dict)):
                clean_row[k] = str(v)
            else:
                clean_row[k] = v
        writer.writerow(clean_row)
    return output.getvalue()
