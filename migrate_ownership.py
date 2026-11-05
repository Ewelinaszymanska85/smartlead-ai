import sqlite3
from pathlib import Path


DB_PATH = Path("smartlead.db")
ADMIN_ID = 1
ADMIN_USERNAME = "ewelina"


def migrate():
    if not DB_PATH.exists():
        raise FileNotFoundError("Nie znaleziono pliku smartlead.db")

    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        # Sprawdzenie konta administratora.
        cursor.execute(
            "SELECT id, username, role FROM users WHERE id = ?",
            (ADMIN_ID,)
        )
        admin = cursor.fetchone()

        if admin != (ADMIN_ID, ADMIN_USERNAME, "admin"):
            raise RuntimeError(
                "Nie znaleziono oczekiwanego konta administratora."
            )

        # Sprawdzenie, czy migracja nie zostaĹ‚a juĹĽ wykonana.
        cursor.execute("PRAGMA table_info(leads)")
        columns = [column[1] for column in cursor.fetchall()]

        if "user_id" in columns:
            print("Kolumna user_id juĹĽ istnieje. Migracja nie zostaĹ‚a wykonana.")
            return

        cursor.execute("SELECT COUNT(*) FROM leads")
        old_count = cursor.fetchone()[0]

        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            CREATE TABLE leads_new (
                id INTEGER NOT NULL PRIMARY KEY,
                created_at DATETIME NOT NULL,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                category VARCHAR(100) NOT NULL,
                priority VARCHAR(20) NOT NULL,
                score INTEGER NOT NULL,
                lead_level VARCHAR(20) NOT NULL,
                status VARCHAR(20) NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            INSERT INTO leads_new (
                id, created_at, name, email, message,
                category, priority, score, lead_level, status, user_id
            )
            SELECT
                id, created_at, name, email, message,
                category, priority, score, lead_level, status, ?
            FROM leads
        """, (ADMIN_ID,))

        cursor.execute("DROP TABLE leads")
        cursor.execute("ALTER TABLE leads_new RENAME TO leads")

        cursor.execute("""
            CREATE INDEX ix_leads_id ON leads (id)
        """)

        # Kontrola wyniku.
        cursor.execute("SELECT COUNT(*) FROM leads")
        new_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM leads WHERE user_id = ?
        """, (ADMIN_ID,))
        assigned_count = cursor.fetchone()[0]

        if old_count != new_count or new_count != assigned_count:
            raise RuntimeError("Kontrola migracji nie powiodĹ‚a siÄ™.")

            connection.commit()

        print("Migracja zakoĹ„czona pomyĹ›lnie.")
        print(f"Liczba zachowanych leadĂłw: {new_count}")
        print(f"LeadĂłw przypisanych do ewelina: {assigned_count}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    migrate()
