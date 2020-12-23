import sqlite3
con = sqlite3.connect("database.db")
print("Connected to database")
con.execute("CREATE TABLE To_do_list(id INTEGER PRIMARY KEY, task_name TEXT, priority TEXT, status TEXT, username TEXT)")
print("table created succesfully")
con.close()
