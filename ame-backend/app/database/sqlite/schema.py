from app.core.config import get_settings
from app.database.sqlite.sqlite import TableConfig, Sqlite3DataModule

TASK_DB_CONFIG = TableConfig(
    name='task',
    columns={
        'id': 'INTEGER',
        'name': 'VARCHAR',
        'priority': 'INTEGER',
        'status': 'INTEGER',
        'create_time': 'DATETIME',
        'update_time': 'DATETIME'
    }
)

_sqlite_db = None


def get_sqlite_db() -> Sqlite3DataModule:
    global _sqlite_db
    if _sqlite_db is None:
        setting = get_settings()
        _sqlite_db = Sqlite3DataModule(
            workdir=str(setting.PROJECT_STORE_PATH),
            db_name='another_me',
            tables=[TASK_DB_CONFIG],
            auto_connect=True
        )
    return _sqlite_db
