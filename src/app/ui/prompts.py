from datetime import datetime

from app.config import RISK_PROFILE_DESCRIPTIONS, VALID_RISK_PROFILES
from app.repositories import client_repository as repo


def prompt(text):
    return input(text).strip()


def prompt_required(text):
    while True:
        value = prompt(text)
        if value:
            return value
        print("This field is required.")


def prompt_float(text, min_value=None):
    while True:
        value = prompt(text)
        try:
            number = float(value)
            if min_value is not None and number < min_value:
                print(f"Value must be at least {min_value}.")
                continue
            return number
        except ValueError:
            print("Please enter a valid number.")


def prompt_int(text, min_value=None):
    while True:
        value = prompt(text)
        try:
            number = int(value)
            if min_value is not None and number < min_value:
                print(f"Value must be at least {min_value}.")
                continue
            return number
        except ValueError:
            print("Please enter a valid integer.")


def prompt_date(text):
    while True:
        value = prompt(f"{text} (YYYY-MM-DD): ")
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Please enter a valid date in YYYY-MM-DD format.")


def print_risk_profile_menu():
    print("\nRisk profile options:")
    for index, profile in enumerate(VALID_RISK_PROFILES, start=1):
        description = RISK_PROFILE_DESCRIPTIONS[profile]
        print(f"  {index}. {profile:10} — {description}")


def prompt_risk_profile(allow_skip=False):
    print_risk_profile_menu()
    prompt_text = "Choose a risk profile (1-4"
    if allow_skip:
        prompt_text += ", Enter to keep current"
    prompt_text += "): "

    while True:
        value = prompt(prompt_text)
        if allow_skip and not value:
            return None
        if value.isdigit():
            choice = int(value)
            if 1 <= choice <= len(VALID_RISK_PROFILES):
                return VALID_RISK_PROFILES[choice - 1]
        if repo.is_valid_risk_profile(value):
            return value
        print("Invalid choice. Please enter a number from 1 to 4.")


def print_search_criterion_menu():
    aum_bounds = repo.get_aum_bounds()
    profile_summary = repo.get_risk_profile_summary()
    managers = repo.list_managers()

    print("\n--- Search by Criterion ---")
    print("\nChoose how to filter clients:\n")

    print("1. Risk profile")
    print("   The client's investment risk tolerance.")
    print("   Available profiles in the database:")
    for row in profile_summary:
        print(f"     - {row['profil_risque']:10} ({row['client_count']} client(s))")
    print_risk_profile_menu()

    print("\n2. Manager ID")
    print("   The portfolio manager (Gestionnaire) assigned to the client.")
    if managers:
        print("   Available managers in the database:")
        for manager in managers:
            print(
                f"     - ID {manager['id_gestionnaire']}: "
                f"{manager['prenom']} {manager['nom']} "
                f"({manager['specialite'] or 'no specialty'})"
            )
    else:
        print("   No managers found in the database.")

    print("\n3. AUM range")
    print("   AUM (Assets Under Management) = total assets managed for a client.")
    if aum_bounds and aum_bounds["client_count"]:
        print(
            f"   Database range: {aum_bounds['min_aum']:,.2f} "
            f"to {aum_bounds['max_aum']:,.2f} "
            f"({aum_bounds['client_count']} client(s))"
        )
    else:
        print("   No client AUM data available yet.")

    print()


def prompt_yes_no(text):
    while True:
        value = prompt(f"{text} (y/n): ").lower()
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")
