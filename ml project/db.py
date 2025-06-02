import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root', 
    'database': 'liver_prediction'
}

try:
    connection = mysql.connector.connect(**DB_CONFIG)
    print("Connection successful!")
    connection.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")

def create_table():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)
        connection.commit()
        print("Table created or already exists.")
    except mysql.connector.Error as err:
        print(f"Error while creating table: {err}")
    finally:
        cursor.close()
        connection.close()



def add_users(username, password):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        # Insert the new user into the database
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        connection.commit()
        print("User added successfully.")
    except mysql.connector.Error as err:
        print(f"Error while adding user: {err}")
    finally:
        cursor.close()
        connection.close()

def get_users(username):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        return user
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()
