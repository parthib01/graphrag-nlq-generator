import sqlite3

def extract_schema(db_path='retail.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']

    schema = {}

    for table in tables:
        # Get column details
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [{
            "name": row[1],
            "type": row[2],
            "pk": bool(row[5])
        } for row in cursor.fetchall()]

        # Get foreign key constraints
        cursor.execute(f"PRAGMA foreign_key_list({table});")
        foreign_keys = [{
            "from": row[3],  # local column
            "to_table": row[2],
            "to_column": row[4]
        } for row in cursor.fetchall()]

        schema[table] = {
            "columns": columns,
            "foreign_keys": foreign_keys
        }

    conn.close()
    return schema
