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
                    note = row[8]
                except IndexError:
                    note = None
                        
                cursor.execute('INSERT INTO logs (number, type, date, route, start, end, notes, mode, userid, operator) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                            (row[1], row[2], row[3], row[4], row[5], row[6], note, mode, userid, row[7]))

        for row in reader:
            if mode == 'victrain':
                if row[2] in ['VLocity', 'N Class', 'Sprinter']:
                    operator = 'V/Line'
                elif row[2] in ["X'Trapolis 100", 'Siemens Nexas', 'EDI Comeng', 'Alstom Comeng', "X'Trapolis 2.0", 'HCMT']:
                    operator = 'Metro Trains Melbourne'
                else: 
                    operator = None
            try:
                note = row[7]
            except IndexError:
                note = None
            cursor.execute('INSERT INTO logs (number, type, date, route, start, end, notes, mode, userid, operator) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (row[1], row[2], row[3], row[4], row[5], row[6], note, mode, userid, operator))


    conn.commit()
    conn.close()
