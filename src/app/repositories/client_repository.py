from mysql.connector import Error

from app.config import ALLOWED_CLIENT_COLUMNS, VALID_RISK_PROFILES
from app.db import db_cursor


def _format_mysql_error(exc):
    message = str(exc)
    if "Duplicate entry" in message and "email" in message:
        return "A client with this email already exists."
    if "foreign key constraint" in message.lower() and "id_gestionnaire" in message.lower():
        return "The specified manager ID does not exist."
    if "chk_client_aum_agressif" in message:
        return "Aggressive clients must have an AUM of at least 100,000."
    if "chk_client_aum" in message:
        return "AUM must be greater than 0."
    if "chk_client_email" in message:
        return "Email must contain '@' and '.'."
    return message


def list_all_clients():
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id_client, nom, prenom, email, aum, profil_risque,
                   date_entree, id_gestionnaire
            FROM Client
            ORDER BY id_client
            """
        )
        return cursor.fetchall()


def get_client_by_id(client_id):
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id_client, nom, prenom, email, aum, profil_risque,
                   date_entree, id_gestionnaire
            FROM Client
            WHERE id_client = %s
            """,
            (client_id,),
        )
        return cursor.fetchone()


def add_client(nom, prenom, email, aum, profil_risque, date_entree, id_gestionnaire):
    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO Client (
                    nom, prenom, email, aum, profil_risque, date_entree, id_gestionnaire
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (nom, prenom, email, aum, profil_risque, date_entree, id_gestionnaire),
            )
            return True, cursor.lastrowid, None
    except Error as exc:
        return False, None, _format_mysql_error(exc)


def update_client(client_id, fields):
    if not fields:
        return False, "No fields to update."

    invalid_fields = set(fields) - ALLOWED_CLIENT_COLUMNS
    if invalid_fields:
        return False, f"Invalid fields: {', '.join(sorted(invalid_fields))}"

    set_clause = ", ".join(f"{column} = %s" for column in fields)
    values = list(fields.values()) + [client_id]

    try:
        with db_cursor() as cursor:
            cursor.execute(
                f"UPDATE Client SET {set_clause} WHERE id_client = %s",
                values,
            )
            if cursor.rowcount == 0:
                return False, f"No client found with ID {client_id}."
            return True, None
    except Error as exc:
        return False, _format_mysql_error(exc)


def delete_client(client_id):
    try:
        with db_cursor() as cursor:
            cursor.execute("DELETE FROM Client WHERE id_client = %s", (client_id,))
            if cursor.rowcount == 0:
                return False, f"No client found with ID {client_id}."
            return True, None
    except Error as exc:
        return False, _format_mysql_error(exc)


def search_by_risk_profile(profil_risque):
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id_client, nom, prenom, email, aum, profil_risque,
                   date_entree, id_gestionnaire
            FROM Client
            WHERE profil_risque = %s
            ORDER BY aum DESC
            """,
            (profil_risque,),
        )
        return cursor.fetchall()


def search_by_manager(manager_id):
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id_client, nom, prenom, email, aum, profil_risque,
                   date_entree, id_gestionnaire
            FROM Client
            WHERE id_gestionnaire = %s
            ORDER BY nom, prenom
            """,
            (manager_id,),
        )
        return cursor.fetchall()


def search_by_aum_range(min_aum, max_aum):
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id_client, nom, prenom, email, aum, profil_risque,
                   date_entree, id_gestionnaire
            FROM Client
            WHERE aum BETWEEN %s AND %s
            ORDER BY aum DESC
            """,
            (min_aum, max_aum),
        )
        return cursor.fetchall()


def search_by_keyword(keyword):
    pattern = f"%{keyword}%"
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id_client, nom, prenom, email, aum, profil_risque,
                   date_entree, id_gestionnaire
            FROM Client
            WHERE nom LIKE %s OR prenom LIKE %s OR email LIKE %s
            ORDER BY nom, prenom
            """,
            (pattern, pattern, pattern),
        )
        return cursor.fetchall()


def get_client_detail(client_id):
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT c.id_client, c.nom, c.prenom, c.email, c.aum, c.profil_risque,
                   c.date_entree, c.id_gestionnaire,
                   g.nom AS manager_last_name, g.prenom AS manager_first_name,
                   g.email AS manager_email, g.specialite AS manager_specialty
            FROM Client c
            JOIN Gestionnaire g ON c.id_gestionnaire = g.id_gestionnaire
            WHERE c.id_client = %s
            """,
            (client_id,),
        )
        client = cursor.fetchone()
        if not client:
            return None, []

        cursor.execute(
            """
            SELECT id_portefeuille, nom, devise_base, strategie,
                   date_creation, valeur_liquidative
            FROM Portefeuille
            WHERE id_client = %s
            ORDER BY id_portefeuille
            """,
            (client_id,),
        )
        portfolios = cursor.fetchall()
        return client, portfolios


def get_statistics():
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT profil_risque, COUNT(*) AS client_count, SUM(aum) AS total_aum
            FROM Client
            GROUP BY profil_risque
            ORDER BY total_aum DESC
            """
        )
        by_profile = cursor.fetchall()

        cursor.execute(
            """
            SELECT COUNT(*) AS total_clients, SUM(aum) AS total_aum,
                   AVG(aum) AS average_aum, MAX(aum) AS max_aum, MIN(aum) AS min_aum
            FROM Client
            """
        )
        global_stats = cursor.fetchone()

        return by_profile, global_stats


def get_top_clients_by_aum(limit):
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id_client, nom, prenom, aum, profil_risque
            FROM Client
            ORDER BY aum DESC
            LIMIT %s
            """,
            (limit,),
        )
        return cursor.fetchall()


def list_managers():
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id_gestionnaire, nom, prenom, email, specialite
            FROM Gestionnaire
            ORDER BY id_gestionnaire
            """
        )
        return cursor.fetchall()


def get_aum_bounds():
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT MIN(aum) AS min_aum, MAX(aum) AS max_aum, COUNT(*) AS client_count
            FROM Client
            """
        )
        return cursor.fetchone()


def get_risk_profile_summary():
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT profil_risque, COUNT(*) AS client_count
            FROM Client
            GROUP BY profil_risque
            ORDER BY FIELD(profil_risque, 'prudent', 'équilibré', 'dynamique', 'agressif')
            """
        )
        return cursor.fetchall()


def is_valid_risk_profile(value):
    return value in VALID_RISK_PROFILES
