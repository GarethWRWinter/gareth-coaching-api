import sqlite3

def export_schema():
    conn = sqlite3.connect("ride_data.db")
    with open("schema.sql", "w") as f:
        for line in conn.iterdump():
            f.write(f"{line}\n")
    conn.close()
    print("✅ schema.sql generated.")

if __name__ == "__main__":
    export_schema()
