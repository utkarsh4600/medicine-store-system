"""
Primary backend entry point.
Run `python backend.py` to start the HTTP Server & API at http://localhost:8000.
Run `python backend.py --cli` to launch the Interactive Console Menu.
"""

import sys
import os

if __name__ == "__main__":
    if "--cli" in sys.argv:
        from cli import main_menu
        main_menu()
    else:
        from server import run_server
        port = int(os.environ.get("PORT", 8000))
        for arg in sys.argv[1:]:
            if arg.isdigit():
                port = int(arg)
        run_server(port)
