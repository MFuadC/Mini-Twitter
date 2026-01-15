import sqlite3
import pandas as pd

conn = sqlite3.connect("database.db")

tables = {
    "users": "SELECT usr, name, email FROM users",
    "posts": "SELECT id, author_usr, content, created_at FROM posts",
    "follows": "SELECT follower_usr, followee_usr, created_at FROM follows"
}

for key, values in tables.items():
    df = pd.read_sql_query(values, conn)
    df.to_csv(f"{key}.csv", index=False)

conn.close()
print("CSV files exported for Visualization.")
