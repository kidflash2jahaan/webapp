import sqlite3
con = sqlite3.connect("database.db")
print("Connected to database")
con.execute("CREATE TABLE Food_tracker(id INTEGER PRIMARY KEY, food_name TEXT, protein TEXT, carbs TEXT, fat TEXT, username TEXT)")
print("table created succesfully")
con.close()
