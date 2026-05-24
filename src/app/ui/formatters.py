def print_separator():
    print("-" * 80)


def format_amount(value):
    if value is None:
        return "N/A"
    return f"{value:,.2f}"


def print_clients(clients):
    if not clients:
        print("No clients found.")
        return

    print_separator()
    for client in clients:
        print(
            f"ID: {client['id_client']} | "
            f"{client['prenom']} {client['nom']} | "
            f"Email: {client['email']} | "
            f"AUM: {client['aum']:,.2f} | "
            f"Profile: {client['profil_risque']} | "
            f"Manager ID: {client['id_gestionnaire']} | "
            f"Entry date: {client['date_entree']}"
        )
    print_separator()
    print(f"Total: {len(clients)} client(s)")


def print_client_detail(client, portfolios):
    print_separator()
    print(f"Client ID     : {client['id_client']}")
    print(f"Name          : {client['prenom']} {client['nom']}")
    print(f"Email         : {client['email']}")
    print(f"AUM           : {client['aum']:,.2f}")
    print(f"Risk profile  : {client['profil_risque']}")
    print(f"Entry date    : {client['date_entree']}")
    print(f"Manager ID    : {client['id_gestionnaire']}")
    print_separator()

    print("\nAssociated manager:")
    print_separator()
    print(f"Name      : {client['manager_first_name']} {client['manager_last_name']}")
    print(f"Email     : {client['manager_email']}")
    print(f"Specialty : {client['manager_specialty'] or 'N/A'}")
    print_separator()

    print("\nAssociated portfolios:")
    if not portfolios:
        print("No portfolios found for this client.")
        return

    print_separator()
    for portfolio in portfolios:
        print(
            f"ID: {portfolio['id_portefeuille']} | "
            f"{portfolio['nom']} | "
            f"Currency: {portfolio['devise_base']} | "
            f"NAV: {portfolio['valeur_liquidative']:,.2f} | "
            f"Strategy: {portfolio['strategie'] or 'N/A'} | "
            f"Created: {portfolio['date_creation']}"
        )
    print_separator()


def print_managers(managers):
    print_separator()
    for manager in managers:
        print(
            f"ID: {manager['id_gestionnaire']} | "
            f"{manager['prenom']} {manager['nom']} | "
            f"Email: {manager['email']} | "
            f"Specialty: {manager['specialite'] or 'N/A'}"
        )
    print_separator()
