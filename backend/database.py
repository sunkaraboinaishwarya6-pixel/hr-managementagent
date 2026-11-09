import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="ishu257",
        database="hr_management_agent"
    )
except mysql.connector.Error as error:
    raise RuntimeError(
        f"Unable to connect to MySQL database 'hr_management_agent': {error}"
    ) from error

print("MySQL connected successfully!")