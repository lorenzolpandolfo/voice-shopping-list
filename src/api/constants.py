USER_SCHEMA = """
        CREATE TABLE IF NOT EXISTS users
        (
            id              TEXT UNIQUE NOT NULL,
            token           TEXT,
            spreadsheet_id  TEXT        NOT NULL,
            spreadsheet_tab TEXT        NOT NULL
        )
        """
