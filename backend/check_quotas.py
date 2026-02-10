import sqlite3
import json

conn = sqlite3.connect('storage/projects.db')
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', [t[0] for t in tables])

# Try to find recent projects
for table_name in [t[0] for t in tables]:
    print(f'\nTable: {table_name}')
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f'Columns: {[col[1] for col in columns]}')
    
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
    row = cursor.fetchone()
    if row:
        print(f'Sample row: {row[:3] if len(row) > 3 else row}...')

conn.close()
