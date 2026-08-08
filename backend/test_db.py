from app.database.connection import check_database_connection

if check_database_connection():
    print("Database connected successfully")
else:
    print("Database connection failed")
