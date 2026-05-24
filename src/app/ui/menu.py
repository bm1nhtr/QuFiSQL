from app.ui.handlers import (
    handle_add_client,
    handle_client_detail,
    handle_delete_client,
    handle_keyword_search,
    handle_list_clients,
    handle_list_managers,
    handle_search_by_criterion,
    handle_statistics,
    handle_update_client,
)
from app.ui.prompts import prompt


def print_main_menu():
    print("\n" + "=" * 40)
    print("  Quant Finance - Client Management")
    print("=" * 40)
    print("1.  Add a new client")
    print("2.  List all clients")
    print("3.  Search by criterion")
    print("4.  Update a client")
    print("5.  Delete a client")
    print("6.  Statistics & rankings")
    print("7.  Search by keyword")
    print("8.  View client detail (with associated data)")
    print("9.  List available managers")
    print("0.  Exit")
    print("=" * 40)


def run_menu():
    actions = {
        "1": handle_add_client,
        "2": handle_list_clients,
        "3": handle_search_by_criterion,
        "4": handle_update_client,
        "5": handle_delete_client,
        "6": handle_statistics,
        "7": handle_keyword_search,
        "8": handle_client_detail,
        "9": handle_list_managers,
    }

    while True:
        print_main_menu()
        choice = prompt("Choose an option: ")

        if choice == "0":
            print("Goodbye!")
            break

        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid option. Please try again.")
