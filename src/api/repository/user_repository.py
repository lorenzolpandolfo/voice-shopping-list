from src.api.constants import USER_SCHEMA
from src.api.database import get_connection
from src.api.model.user_model import User


class UserRepository:
    def __init__(self):
        self._create_table()

    @staticmethod
    def _create_table():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(USER_SCHEMA)
        conn.commit()
        conn.close()

    @staticmethod
    def create(user: User) -> User:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (id, token, spreadsheet_id, spreadsheet_tab) VALUES (?, ?, ?, ?)",
            (user.id, user.token, user.spreadsheet_id, user.spreadsheet_tab),
        )
        conn.commit()
        conn.close()
        return UserRepository.find_by_id(user.id)

    @staticmethod
    def update(user: User) -> User | None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET token = ? WHERE id = ?", (user.token, user.id))
        conn.commit()
        conn.close()
        return UserRepository.find_by_id(user.id)

    @staticmethod
    def find_all() -> list[User]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, token FROM users")
        rows = cursor.fetchall()
        conn.close()
        return [User(id=row[0], token=row[1]) for row in rows]

    @staticmethod
    def find_by_id(user_id: str) -> User | None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, token, spreadsheet_id, spreadsheet_tab FROM users WHERE id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(
                id=row[0], token=row[1], spreadsheet_id=row[2], spreadsheet_tab=row[3]
            )
        return None

    @staticmethod
    def delete(user_id: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
