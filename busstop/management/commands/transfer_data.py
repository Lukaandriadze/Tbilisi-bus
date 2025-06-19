from django.core.management.base import BaseCommand
import sqlite3
import os


class Command(BaseCommand):
    help = "Transfer data from db_backup.sqlite3 to db.sqlite3 for buses_buses and busstop_busstop"

    def handle(self, *args, **options):
        backup_db = "db_backup.sqlite3"
        new_db = "db.sqlite3"

        # Check if files exist
        if not os.path.exists(backup_db):
            self.stdout.write(self.style.ERROR("❌ Backup database 'db_backup.sqlite3' not found."))
            return
        if not os.path.exists(new_db):
            self.stdout.write(self.style.ERROR("❌ New database 'db.sqlite3' not found. Run `migrate` first."))
            return

        # Connect to both databases
        try:
            source_conn = sqlite3.connect(backup_db)
            dest_conn = sqlite3.connect(new_db)
            source_cursor = source_conn.cursor()
            dest_cursor = dest_conn.cursor()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to connect to databases: {e}"))
            return

        tables = ["buses_buses", "busstop_busstop"]

        for table in tables:
            try:
                # Get rows from source
                source_cursor.execute(f"SELECT * FROM {table}")
                rows = source_cursor.fetchall()

                # Get column names
                source_cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in source_cursor.fetchall()]
                column_str = ", ".join(columns)
                placeholders = ", ".join(["?"] * len(columns))

                # Insert into destination
                dest_cursor.executemany(
                    f"INSERT INTO {table} ({column_str}) VALUES ({placeholders})",
                    rows
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Copied {len(rows)} rows into {table}"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ Error copying table {table}: {e}"))

        # Commit and close connections
        dest_conn.commit()
        source_conn.close()
        dest_conn.close()

        self.stdout.write(self.style.SUCCESS("✅ Data transfer complete."))
