import sqlite3


# make the connection
connection = sqlite3.connect("sqlite.db")
cursor = connection.cursor()

# 1.Create a table
cursor.execute("""
            CREATE TABLE IF NOT EXISTS shipment (
               id INTEGER PRIMARY KEY,
               content TEXT,
               weight REAL,
               status TEXT
            )
""")

# cursor.execute("DROP TABLE IF EXISTS shipment")
# connection.commit()

# 2. Add shipment data
cursor.execute("""
    INSERT INTO shipment
    VALUES (1241, 'Missile', 18.5, 'placed')
""")
connection.commit()

# 3. Read a shipment by id
# cursor.execute("""
#     SELECT * FROM shipment
#     WHERE id = 1241
# """)
# result = cursor.fetchall()
# print(result)

# 4. Delete a shipment
# cursor.execute("""
#     DELETE FROM shipment
#     WHERE id = 1243
# """)
# connection.commit()

# close the connection when done
connection.close()
