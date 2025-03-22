import sqlite3

# Connect to your actual database file
conn = sqlite3.connect('lifestyle_db.sqlite')  # Change to your actual database name
cursor = conn.cursor()

# Check the columns in the 'user' table
cursor.execute("PRAGMA table_info(user);")
columns = cursor.fetchall()

# Print column names
for column in columns:
    print(column)

# Commit and close the connection
conn.commit()
conn.close()

