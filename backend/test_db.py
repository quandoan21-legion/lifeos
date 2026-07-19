from sqlalchemy import text

from app.database.connection import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(result.fetchone())
        print("Database connected successfully")

except Exception as error:
    print("Database connection failed:")
    print(error)
