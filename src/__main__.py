import sys
from pathlib import Path

_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from app.db import test_connection
from app.ui.menu import run_menu


def main():
    print("Quant Finance Console Application")
    print("Connecting to MySQL...")

    success, error = test_connection()
    if not success:
        print("Failed to connect to the database.")
        print(f"Error: {error}")
        print("\nPlease check:")
        print("  - MySQL server is running")
        print("  - Database 'quant_finance' exists (run sql/script_creation.sql)")
        print("  - Credentials in .env are correct (copy from .env.example)")
        return

    print("Connected successfully.\n")
    run_menu()


if __name__ == "__main__":
    main()
