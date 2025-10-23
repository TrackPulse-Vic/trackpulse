import sqlite3

def logTrip(user, mode, date, vehicleNumber, vehicleType, start, end, line, operator, note, tags):
    try:
        conn = sqlite3.connect('databases/logs.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT,
                mode TEXT,
                date TEXT,
                operatorTEXT,
                number TEXT,
                type TEXT,
                route TEXT,
                start TEXT,
                end TEXT,
                notes TEXT,
                tags TEXT
            )
        ''')
        
        cursor.execute('''
            INSERT INTO logs (userid, mode, date, operator, number, type, route, start, end, notes, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user, mode, date, operator, vehicleNumber, vehicleType, line, start, end, note, tags))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding trip to Database: {e}")
        return False