import sqlite3

def addUser(sub, name, email):
    conn = sqlite3.connect('databases/users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, sub TEXT, name TEXT, email TEXT)''')
    c.execute("SELECT * FROM users WHERE sub = ?", (sub,))
    if c.fetchone() is None:
        c.execute("INSERT INTO users (sub, name, email) VALUES (?, ?, ?)", (sub, name, email))
        conn.commit()
        print("User added to the database successfully.")
    else:
        print("User already exists in the database.")
    conn.close()
