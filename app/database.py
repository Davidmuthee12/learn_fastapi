import sqlite3


# make the connection
connection = sqlite3.connect("sqlite.db")
cursor = connection.cursor()

# 1.Create a table
cursor.execute("""
            CREATE TABLE IF NOT EXISTS shipment (
               id INTEGER,
               content TEXT,
               weight REAL,
               status TEXT
            )
""")


# close the connection when done
connection.close()
