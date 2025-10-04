import csv
import sqlite3

def convertLogs(filePath, mode, userid):
    print(f"Userid: {userid}")
    conn = sqlite3.connect('databases/logs.db')
    cursor = conn.cursor()

    with open(filePath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
         if mode == 'vicbus':
             
        
        for row in reader:
            try:
                note = row[7]
            except IndexError:
                note = None
            cursor.execute('INSERT INTO logs (number, type, date, route, start, end, notes, mode, userid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (row[1], row[2], row[3], row[4], row[5], row[6], note, mode, userid))


    conn.commit()
    conn.close()
