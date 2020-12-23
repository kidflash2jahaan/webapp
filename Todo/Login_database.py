import sqlite3
con = sqlite3.connect("database.db")
print("Connected to database")
con.execute("CREATE TABLE user(id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, email TEXT, password TEXT)")
print("table created succesfully")
con.close()
