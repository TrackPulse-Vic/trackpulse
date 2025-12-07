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
        return cursor.lastrowid
    except Exception as e:
        print(f"Error adding trip to Database: {e}")
        return False
    finally:
        conn.close()
    
def getOperator(mode, vType):
    if mode == 'victrain':
        if vType in ['VLocity', 'N Class', 'Sprinter']:
            operator = 'V/Line'
        elif vType in ["X'Trapolis 100", 'Siemens Nexas', 'EDI Comeng', 'Alstom Comeng', "X'Trapolis 2.0", 'HCMT']:
            operator = 'Metro Trains Melbourne'
        else: 
            operator = None
            
    elif mode == 'victram':
        if vType in ['G Class','W Class','Z Class', "A Class", 'B Class','C Class', 'C2 Class', 'D Class','E Class']:
            operator = 'Yarra Trams'
        else:
            operator = None
            
    elif mode == 'satrain':
        if vType == 'NR Class':
            operator = 'Journey Beyond Rail'
        elif vType in ['3000 Class', '3100 Class', '4000 Class']:
            operator = 'Adelaide Metro'
        else:
            operator = None
    
    elif mode == 'sabus':
        operator = 'Adelaide Metro'
    
    elif mode == 'satram':
        operator = 'Adelaide Metro'
        
    elif mode == 'nswtrain':
        if vType in ['Metropolis Stock']:
            operator = 'Sydney Metro'
        elif vType in ['Waratah', 'OSCAR', 'Hunter', 'K Set', 'Millennium', 'Hunter railcar', 'Tangara', 'V Set', 'D Set']:
            operator = 'Sydney Trains'
        elif vType in ['XPT', 'Xplorer', 'Endeavour railcar']:
            operator = 'NSW TrainLink'
        else:
            operator = None
        
    else: 
        operator = None
    return operator