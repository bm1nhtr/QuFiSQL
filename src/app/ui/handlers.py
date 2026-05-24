from datetime import datetime

from app.config import VALID_RISK_PROFILES
from app.repositories import client_repository as repo
from app.ui.formatters import (
    format_amount,
    print_client_detail,
    print_clients,
    print_managers,
    print_separator,
)
from app.ui.prompts import (
    print_search_criterion_menu,
    prompt,
    prompt_date,
    prompt_float,
    prompt_int,
    prompt_required,
    prompt_risk_profile,
    prompt_yes_no,
)


def handle_add_client():
    print("\n--- Add New Client ---")
    nom = prompt_required("Last name: ")
    prenom = prompt_required("First name: ")
    email = prompt_required("Email: ")
    print("\nAUM (Assets Under Management) = total assets managed for the client.")
    aum = prompt_float("AUM: ", min_value=0.01)
    profil_risque = prompt_risk_profile()
    date_entree = prompt_date("Entry date")
    id_gestionnaire = prompt_int("Manager ID: ", min_value=1)

    success, client_id, error = repo.add_client(
        nom, prenom, email, aum, profil_risque, date_entree, id_gestionnaire
    )
    if success:
        print(f"Client added successfully with ID {client_id}.")
    else:
        print(f"Failed to add client: {error}")


def handle_list_clients():
    print("\n--- All Clients ---")
    clients = repo.list_all_clients()
    print_clients(clients)


def handle_search_by_criterion():
    print_search_criterion_menu()
    choice = prompt("Choose criterion (1-3): ")

    if choice == "1":
        profil_risque = prompt_risk_profile()
        clients = repo.search_by_risk_profile(profil_risque)
        print(f"\nClients with risk profile '{profil_risque}':")
        print_clients(clients)
    elif choice == "2":
        print("\nTip: use option 9 from the main menu to view all managers.")
        manager_id = prompt_int("Manager ID: ", min_value=1)
        clients = repo.search_by_manager(manager_id)
        print(f"\nClients managed by manager ID {manager_id}:")
        print_clients(clients)
    elif choice == "3":
        aum_bounds = repo.get_aum_bounds()
        if aum_bounds and aum_bounds["client_count"]:
            print(
                f"\nAUM in database ranges from {aum_bounds['min_aum']:,.2f} "
                f"to {aum_bounds['max_aum']:,.2f}."
            )
        min_aum = prompt_float("Minimum AUM: ", min_value=0)
        max_aum = prompt_float("Maximum AUM: ", min_value=min_aum)
        clients = repo.search_by_aum_range(min_aum, max_aum)
        print(f"\nClients with AUM between {min_aum:,.2f} and {max_aum:,.2f}:")
        print_clients(clients)
    else:
        print("Invalid choice.")


def handle_update_client():
    print("\n--- Update Client ---")
    client_id = prompt_int("Client ID to update: ", min_value=1)
    client = repo.get_client_by_id(client_id)
    if not client:
        print(f"No client found with ID {client_id}.")
        return

    print("\nCurrent client data:")
    print_clients([client])
    print("\nLeave a field blank to keep its current value.")

    fields = {}
    nom = prompt(f"Last name [{client['nom']}]: ")
    if nom:
        fields["nom"] = nom

    prenom = prompt(f"First name [{client['prenom']}]: ")
    if prenom:
        fields["prenom"] = prenom

    email = prompt(f"Email [{client['email']}]: ")
    if email:
        fields["email"] = email

    aum_input = prompt(f"AUM [{client['aum']}]: ")
    if aum_input:
        try:
            aum = float(aum_input)
            if aum <= 0:
                print("AUM must be greater than 0. Update cancelled.")
                return
            fields["aum"] = aum
        except ValueError:
            print("Invalid AUM. Update cancelled.")
            return

    profil_risque = prompt(
        f"Risk profile [{client['profil_risque']}] (Enter to keep, or type 'menu'): "
    )
    if profil_risque.lower() == "menu":
        selected_profile = prompt_risk_profile()
        fields["profil_risque"] = selected_profile
    elif profil_risque:
        if profil_risque.isdigit():
            choice = int(profil_risque)
            if 1 <= choice <= len(VALID_RISK_PROFILES):
                fields["profil_risque"] = VALID_RISK_PROFILES[choice - 1]
            else:
                print("Invalid risk profile number. Update cancelled.")
                return
        elif repo.is_valid_risk_profile(profil_risque):
            fields["profil_risque"] = profil_risque
        else:
            print("Invalid risk profile. Update cancelled.")
            return

    date_entree = prompt(f"Entry date [{client['date_entree']}]: ")
    if date_entree:
        try:
            datetime.strptime(date_entree, "%Y-%m-%d")
            fields["date_entree"] = date_entree
        except ValueError:
            print("Invalid date. Update cancelled.")
            return

    manager_input = prompt(f"Manager ID [{client['id_gestionnaire']}]: ")
    if manager_input:
        try:
            fields["id_gestionnaire"] = int(manager_input)
        except ValueError:
            print("Invalid manager ID. Update cancelled.")
            return

    success, error = repo.update_client(client_id, fields)
    if success:
        print("Client updated successfully.")
    else:
        print(f"Failed to update client: {error}")


def handle_delete_client():
    print("\n--- Delete Client ---")
    client_id = prompt_int("Client ID to delete: ", min_value=1)
    client = repo.get_client_by_id(client_id)
    if not client:
        print(f"No client found with ID {client_id}.")
        return

    print("\nClient to delete:")
    print_clients([client])
    if not prompt_yes_no("Are you sure you want to delete this client?"):
        print("Deletion cancelled.")
        return

    success, error = repo.delete_client(client_id)
    if success:
        print("Client deleted successfully.")
    else:
        print(f"Failed to delete client: {error}")


def handle_statistics():
    print("\n--- Statistics & Rankings ---")
    by_profile, global_stats = repo.get_statistics()

    print("\nGlobal statistics:")
    print_separator()
    print(f"Total clients : {global_stats['total_clients'] or 0}")
    print(f"Total AUM     : {format_amount(global_stats['total_aum'])}")
    print(f"Average AUM   : {format_amount(global_stats['average_aum'])}")
    print(f"Max AUM       : {format_amount(global_stats['max_aum'])}")
    print(f"Min AUM       : {format_amount(global_stats['min_aum'])}")
    print_separator()

    if not global_stats["total_clients"]:
        print("No client data available for rankings.")
        return

    print("\nBreakdown by risk profile:")
    print_separator()
    for row in by_profile:
        print(
            f"{row['profil_risque']:12} | "
            f"Clients: {row['client_count']} | "
            f"Total AUM: {format_amount(row['total_aum'])}"
        )
    print_separator()

    limit = prompt_int("\nHow many top clients to display? ", min_value=1)
    top_clients = repo.get_top_clients_by_aum(limit)
    print(f"\nTop {limit} clients by AUM:")
    print_separator()
    for rank, client in enumerate(top_clients, start=1):
        print(
            f"#{rank} | ID: {client['id_client']} | "
            f"{client['prenom']} {client['nom']} | "
            f"AUM: {client['aum']:,.2f} | Profile: {client['profil_risque']}"
        )
    print_separator()


def handle_keyword_search():
    print("\n--- Keyword Search ---")
    keyword = prompt_required("Enter keyword (searches name, first name, email): ")
    clients = repo.search_by_keyword(keyword)
    print(f"\nResults for keyword '{keyword}':")
    print_clients(clients)


def handle_client_detail():
    print("\n--- Client Detail ---")
    client_id = prompt_int("Client ID: ", min_value=1)
    client, portfolios = repo.get_client_detail(client_id)
    if not client:
        print(f"No client found with ID {client_id}.")
        return

    print_client_detail(client, portfolios)


def handle_list_managers():
    print("\n--- Available Managers ---")
    managers = repo.list_managers()
    print_managers(managers)
