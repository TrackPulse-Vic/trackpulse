import sqlite3


def getLogs(user=None, mode=None, line=None, start=None, end=None, type=None, date=None, number=None, id=None, order='DESC'):
    conn = sqlite3.connect('databases/logs.db')
    cursor = conn.cursor()
    query = "SELECT * FROM logs WHERE 1=1"
    params = []
    if user:
        query += " AND userid=?"
        params.append(user)
    if mode:
        query += " AND mode=?"
        params.append(mode)
    if line:
        query += " AND route=?"
        params.append(line)
    if start:
        query += " AND start=?"
        params.append(start)
    if end:
        query += " AND end=?"
        params.append(end)
    if type:
        query += " AND type=?"
        params.append(type)
    if date:
        query += " AND date=?"
        params.append(date)
    if number:
        query += " AND number=?"
        params.append(number)
    if id:
        query += " AND id=?"
        params.append(id)

    # validate order and append ORDER BY
    order = (order or 'DESC').upper()
    if order not in ('ASC', 'DESC'):
        order = 'DESC'
    query += f" ORDER BY date {order}"

    cursor.execute(query, params)
    logs = cursor.fetchall()
    conn.close()
    return logs

def deleteLog(logID):
    try:
        conn = sqlite3.connect('databases/logs.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM logs WHERE id=?", (logID,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
        return False

def updateLog(logID, origin, destination, date, line, vehicle, number, note):
    try:
        conn = sqlite3.connect('databases/logs.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE logs
            SET date=?, route=?, start=?, end=?, type=?, number=?, notes=?
            WHERE id=?
        ''', (date, line, origin, destination, vehicle, number, note, logID))
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated
    except sqlite3.Error:
        return False