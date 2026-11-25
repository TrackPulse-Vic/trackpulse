import sqlite3

USERS_DB_PATH = 'databases/users.db'


def _connect():
    conn = sqlite3.connect(USERS_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, sub TEXT UNIQUE, name TEXT, email TEXT,
                     private INTEGER NOT NULL DEFAULT 1)''')
    # migrate databases created before the privacy column existed
    columns = {row['name'] for row in conn.execute('PRAGMA table_info(users)')}
    if 'private' not in columns:
        conn.execute('ALTER TABLE users ADD COLUMN private INTEGER NOT NULL DEFAULT 1')
        conn.commit()
    return conn


def addUser(sub, name, email):
    conn = _connect()
    try:
        existing = conn.execute("SELECT id FROM users WHERE sub = ?", (sub,)).fetchone()
        if existing is None:
            conn.execute("INSERT INTO users (sub, name, email) VALUES (?, ?, ?)", (sub, name, email))
            print("User added to the database successfully.")
        else:
            # keep display name and email in sync with the identity provider
            conn.execute("UPDATE users SET name = ?, email = ? WHERE sub = ?", (name, email, sub))
        conn.commit()
    finally:
        conn.close()


def _row_to_user(row):
    if row is None:
        return None
    return {
        'id': row['id'],
        'sub': row['sub'],
        'name': row['name'],
        'email': row['email'],
        'private': bool(row['private']),
    }


def getUser(sub=None, user_id=None):
    '''Look up a user by their auth0 sub or by their numeric profile id.'''
    conn = _connect()
    try:
        if sub is not None:
            row = conn.execute("SELECT * FROM users WHERE sub = ?", (sub,)).fetchone()
        elif user_id is not None:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        else:
            return None
        return _row_to_user(row)
    finally:
        conn.close()


def setPrivacy(sub, private):
    conn = _connect()
    try:
        cursor = conn.execute("UPDATE users SET private = ? WHERE sub = ?", (1 if private else 0, sub))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
