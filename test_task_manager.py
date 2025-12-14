import pytest
import mysql.connector
import os
from dotenv import load_dotenv

from task_manager import (
    vytvoreni_tabulky,
    pridat_ukol_db,
    aktualizovat_ukol_db,
    odstranit_ukol_db,
    ziskat_ukoly_db,
)

# =========================
# KONFIGURACE
# =========================
load_dotenv()

TEST_DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),  # stejná DB jako v hlavním kódu
}

# =========================
# PŘIPOJENÍ K DATABÁZI
# =========================
@pytest.fixture(scope="function")
def test_conn():
    conn = mysql.connector.connect(**TEST_DB_CONFIG)
    vytvoreni_tabulky(conn)

    cursor = conn.cursor()
    cursor.execute("DELETE FROM ukoly")
    conn.commit()
    cursor.close()

    yield conn
    conn.close()

# =========================
# TESTY PŘIDÁNÍ ÚKOLU
# =========================
# pozitvní test přidání úkolu
def test_pridat_ukol_pozitivni(test_conn):
    new_id = pridat_ukol_db(test_conn, "Test úkol", "Popis")

    cursor = test_conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ukoly WHERE id = %s", (new_id,))
    row = cursor.fetchone()
    cursor.close()

    assert row is not None
    assert row["nazev"] == "Test úkol"
    assert row["popis"] == "Popis"
    assert row["stav"] == "nezahájeno"

# negativní test přidání úkolu s prázdným názvem
def test_pridat_ukol_negativni_prazdny_nazev(test_conn):
    
    pocet_pred = len(ziskat_ukoly_db(test_conn))

    pocet_po = len(ziskat_ukoly_db(test_conn))

    assert pocet_po == pocet_pred

# =========================
# TESTY AKTUALIZACE
# =========================
# pozitivní test aktualizace stavu úkolu
def test_aktualizovat_ukol_pozitivni(test_conn):
    task_id = pridat_ukol_db(test_conn, "Úkol", "Popis")
    aktualizovat_ukol_db(test_conn, task_id, "hotovo")

    cursor = test_conn.cursor(dictionary=True)
    cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (task_id,))
    row = cursor.fetchone()
    cursor.close()

    assert row["stav"] == "hotovo"

# negativní test aktualizace neexistujícího úkolu
def test_aktualizovat_ukol_neexistujici_id(test_conn):
    
    aktualizovat_ukol_db(test_conn, 9999, "hotovo")

    assert len(ziskat_ukoly_db(test_conn)) == 0

# =========================
# TESTY ODSTRANĚNÍ
# =========================
# pozitivní test odstranění úkolu
def test_odstranit_ukol_pozitivni(test_conn):
    task_id = pridat_ukol_db(test_conn, "Mazání", "Popis")
    odstranit_ukol_db(test_conn, task_id)

    assert len(ziskat_ukoly_db(test_conn)) == 0

# negativní test odstranění neexitujícího úkolu
def test_odstranit_ukol_neexistujici_id(test_conn):
    odstranit_ukol_db(test_conn, 123456)

    assert len(ziskat_ukoly_db(test_conn)) == 0
