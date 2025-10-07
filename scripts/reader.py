import sqlite3


def getLogs(user=None, mode=None, line=None, start=None, end=None, type=None, date=None, number=None):
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
        query += " AND line=?"
        params.append(line)
    if start:
        query += " AND date>=?"
        params.append(start)
    if end:
        query += " AND date<=?"
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
    cursor.execute(query, params)
    logs = cursor.fetchall()
    conn.close()
    return logs