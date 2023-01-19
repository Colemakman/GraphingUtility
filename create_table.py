import sqlite3

# Connect to the database
conn = sqlite3.connect("graphs.db")

# Create a cursor
cursor = conn.cursor()

# Execute the CREATE TABLE statement
cursor.execute('''CREATE TABLE graphs (
                    graphId TEXT PRIMARY KEY,
                    data TEXT,
                    position TEXT,
                    name TEXT
                    )''')

# Commit the changes to the database
conn.commit()

# Close the connection
conn.close()

# Make the Users table

# Connect to the database
conn = sqlite3.connect("graphs.db")

# Create a cursor
cursor = conn.cursor()

# Execute the CREATE TABLE statement
cursor.execute('''CREATE TABLE users (
                    userId TEXT,
                    graphId TEXT PRIMARY KEY,
                    FOREIGN KEY(graphId) REFERENCES graphs(graphId)
                    )''')

# Commit the changes to the database
conn.commit()

# Close the connection
conn.close()

