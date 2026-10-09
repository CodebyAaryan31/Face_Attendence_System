import subprocess
import sys

from src.database import initialize_database


# ==========================================
# APPLICATION CONFIGURATION
# ==========================================

def print_header():

    print("\n")
    print("=" * 50)
    print("          FACE ATTENDANCE SYSTEM")
    print("=" * 50)


# ==========================================
# RUN A PROJECT MODULE
# ==========================================

def run_module(module_name):

    try:

        subprocess.run(
            [sys.executable, "-m", module_name],
            check=False
        )

    except KeyboardInterrupt:

        print("\nOperation interrupted.")

    except Exception as error:

        print(f"\nError: {error}")

    input("\nPress Enter to return to the main menu...")


# ==========================================
# MAIN MENU
# ==========================================

def main():

    initialize_database()

    while True:

        print_header()

        print("1. Register a Student")
        print("2. Train Face Recognition Model")
        print("3. Start Attendance Scanner")
        print("4. View Attendance Reports")
        print("5. Exit")

        choice = input(
            "\nChoose an option (1-5): "
        ).strip()

        if choice == "1":

            run_module("src.register")

        elif choice == "2":

            run_module("src.train_model")

        elif choice == "3":

            run_module("src.attendance_scanner")

        elif choice == "4":

            run_module("src.reports")

        elif choice == "5":

            print("\nThank you for using Face Attendance System!")
            break

        else:

            print("\nInvalid choice. Please select 1-5.")

            input("Press Enter to continue...")


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

if __name__ == "__main__":

    main()