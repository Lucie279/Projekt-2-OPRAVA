import mysql.connector
import logging
import os
from dotenv import load_dotenv

# =========================
# KONFIGURACE
# =========================
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

DB_NAME = os.getenv("DB_NAME")

logging.basicConfig(level=logging.ERROR)


# =========================
# DB FUNKCE
# =========================
def pripojeni_db(db_name=None):
    try:
        return mysql.connector.connect(
            **DB_CONFIG,
            database=db_name
        )
    except mysql.connector.Error as err:
        logging.error(err)
        return None


def vytvor_databazi():
    conn = pripojeni_db()
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.close()
    conn.close()


def vytvoreni_tabulky(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(255) NOT NULL,
            popis TEXT NOT NULL,
            stav ENUM('nezahájeno','probíhá','hotovo') DEFAULT 'nezahájeno',
            datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()


def pridat_ukol_db(conn, nazev, popis):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)",
        (nazev, popis)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    return new_id


def ziskat_ukoly_db(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, nazev, popis, stav
        FROM ukoly
        WHERE stav IN ('nezahájeno', 'probíhá')
        ORDER BY id
    """)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def existuje_ukol(conn, id_ukolu):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM ukoly WHERE id = %s", (id_ukolu,))
    exists = cursor.fetchone() is not None
    cursor.close()
    return exists


def aktualizovat_ukol_db(conn, id_ukolu, novy_stav):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE ukoly SET stav = %s WHERE id = %s",
        (novy_stav, id_ukolu)
    )
    conn.commit()
    cursor.close()


def odstranit_ukol_db(conn, id_ukolu):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
    conn.commit()
    cursor.close()


# =========================
# UI FUNKCE
# =========================
def zobrazit_ukoly(conn):
    ukoly = ziskat_ukoly_db(conn)

    if not ukoly:
        print("\nSeznam úkolů je prázdný.\n")
        return False

    print("\n------------------------------")
    for u in ukoly:
        print(f"ID: {u['id']}")
        print(f"Název: {u['nazev']}")
        print(f"Popis: {u['popis']}")
        print(f"Stav: {u['stav']}")
        print("------------------------------")
    print()
    return True


def pridat_ukol(conn):
    nazev = input("Zadejte název úkolu: ").strip()
    popis = input("Zadejte popis úkolu: ").strip()

    if not nazev or not popis:
        print("\nNázev i popis jsou povinné.\n")
        return

    new_id = pridat_ukol_db(conn, nazev, popis)
    print(f"\nÚkol byl přidán. ID úkolu: {new_id}\n")


def aktualizovat_ukol(conn):
    if not zobrazit_ukoly(conn):
        return

    try:
        id_ukolu = int(input("Zadejte ID úkolu: "))
    except ValueError:
        print("\nNeplatné ID.\n")
        return

    if not existuje_ukol(conn, id_ukolu):
        print(f"\nÚkol s ID {id_ukolu} neexistuje.\n")
        return

    print("\n1. Probíhá")
    print("2. Hotovo\n")

    volba = input("Nový stav (1–2): ").strip()

    if volba == "1":
        novy_stav = "probíhá"
    elif volba == "2":
        novy_stav = "hotovo"
    else:
        print("\nNeplatná volba.\n")
        return

    aktualizovat_ukol_db(conn, id_ukolu, novy_stav)
    print(f"\nÚkol {id_ukolu} byl aktualizován na stav '{novy_stav}'.\n")


def odstranit_ukol(conn):
    if not zobrazit_ukoly(conn):
        return

    try:
        id_ukolu = int(input("Zadejte ID úkolu ke smazání: "))
    except ValueError:
        print("\nNeplatné ID.\n")
        return

    if not existuje_ukol(conn, id_ukolu):
        print(f"\nÚkol s ID {id_ukolu} neexistuje.\n")
        return

    odstranit_ukol_db(conn, id_ukolu)
    print(f"\nÚkol {id_ukolu} byl odstraněn.\n")


# =========================
# HLAVNÍ MENU
# =========================
def hlavni_menu():
    vytvor_databazi()
    conn = pripojeni_db(DB_NAME)

    if not conn:
        print("Nepodařilo se připojit k databázi.")
        return

    vytvoreni_tabulky(conn)

    while True:
        print("\n====================")
        print("   HLAVNÍ MENU")
        print("====================")
        print("1. Přidat úkol")
        print("2. Zobrazit úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Ukončit program")

        volba = input("Volba (1–5): ").strip()
        print()

        if volba == "1":
            pridat_ukol(conn)
        elif volba == "2":
            zobrazit_ukoly(conn)
        elif volba == "3":
            aktualizovat_ukol(conn)
        elif volba == "4":
            odstranit_ukol(conn)
        elif volba == "5":
            print("Program ukončen.\n")
            break
        else:
            print("Neplatná volba.\n")

    conn.close()


if __name__ == "__main__":
    hlavni_menu()
