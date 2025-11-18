from __future__ import annotations

import os
import sqlite3
import threading
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from app.core.logger import get_logger

logger = get_logger(__name__)

_write_lock = threading.Lock()


@dataclass
class TableConfig:
    """表配置数据类

    Attributes:
        name: 表名
        columns: 列定义字典，格式为 {列名: SQL类型定义}
        primary_key: 主键列名，默认为 'id'
        auto_increment: 主键是否自动递增，默认为 True
    """
    name: str
    columns: Dict[str, str]
    primary_key: str = 'id'
    auto_increment: bool = True

    def get_create_sql(self) -> str:
        """生成创建表的 SQL 语句"""
        col_defs = []

        # 添加主键
        if self.auto_increment:
            col_defs.append(f"{self.primary_key} INTEGER PRIMARY KEY AUTOINCREMENT")
        else:
            col_defs.append(f"{self.primary_key} {self.columns.get(self.primary_key, 'INTEGER')} PRIMARY KEY")

        # 添加其他列
        for col_name, col_type in self.columns.items():
            if col_name != self.primary_key:
                col_defs.append(f"{col_name} {col_type}")

        return f"CREATE TABLE IF NOT EXISTS {self.name} ({', '.join(col_defs)})"


@dataclass
class QueryResult:
    """查询结果封装类

    提供属性访问和方法访问两种方式
    """
    columns: List[str]
    rows: List[Tuple]

    def __getitem__(self, index: int) -> Dict[str, Any]:
        """通过索引访问行数据"""
        if 0 <= index < len(self.rows):
            return dict(zip(self.columns, self.rows[index]))
        raise IndexError(f"Index {index} out of range")

    def __len__(self) -> int:
        """返回结果行数"""
        return len(self.rows)

    def __iter__(self):
        """迭代器支持"""
        for row in self.rows:
            yield dict(zip(self.columns, row))

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """转换为字典列表"""
        return [dict(zip(self.columns, row)) for row in self.rows]

    def first(self) -> Optional[Dict[str, Any]]:
        """获取第一行"""
        return self[0] if len(self.rows) > 0 else None

    def all(self) -> List[Dict[str, Any]]:
        """获取所有行"""
        return self.to_dict_list()


class TableAccessor:
    """表访问器，提供对特定表的操作接口"""

    def __init__(self, db_module: 'Sqlite3DataModule', table_name: str):
        self._db = db_module
        self._table_name = table_name

    def insert(self, data: Dict[str, Any], ignore_conflict: bool = False) -> int:
        """插入数据

        Args:
            data: 要插入的数据字典
            ignore_conflict: 是否忽略冲突（使用 INSERT OR IGNORE）

        Returns:
            插入行的 ID
        """
        return self._db.insert(self._table_name, data, ignore_conflict)

    def insert_many(self, data_list: List[Dict[str, Any]], ignore_conflict: bool = False) -> int:
        """批量插入数据

        Args:
            data_list: 要插入的数据字典列表
            ignore_conflict: 是否忽略冲突

        Returns:
            插入的行数
        """
        return self._db.insert_many(self._table_name, data_list, ignore_conflict)

    def update(self, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """更新数据

        Args:
            data: 要更新的数据字典
            where: 条件字典

        Returns:
            影响的行数
        """
        return self._db.update(self._table_name, data, where)

    def delete(self, where: Dict[str, Any]) -> int:
        """删除数据

        Args:
            where: 条件字典

        Returns:
            删除的行数
        """
        return self._db.delete(self._table_name, where)

    def select(self,
               columns: Optional[List[str]] = None,
               where: Optional[Dict[str, Any]] = None,
               order_by: Optional[str] = None,
               limit: Optional[int] = None,
               offset: Optional[int] = None) -> QueryResult:
        """查询数据

        Args:
            columns: 要查询的列名列表，None 表示查询所有列
            where: 条件字典
            order_by: 排序字段
            limit: 限制返回行数
            offset: 偏移量

        Returns:
            QueryResult 对象
        """
        return self._db.select(self._table_name, columns, where, order_by, limit, offset)

    def select_one(self, where: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """查询单行数据

        Args:
            where: 条件字典

        Returns:
            字典形式的行数据，如果不存在则返回 None
        """
        result = self.select(where=where, limit=1)
        return result.first()

    def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        """统计行数

        Args:
            where: 条件字典

        Returns:
            符合条件的行数
        """
        return self._db.count(self._table_name, where)

    def exists(self, where: Dict[str, Any]) -> bool:
        """检查是否存在符合条件的记录

        Args:
            where: 条件字典

        Returns:
            是否存在
        """
        return self.count(where) > 0


class Sqlite3DataModule:
    """SQLite 数据库封装类

    提供便捷的数据库操作接口，将传统 SQL 语句转换为 Python 方法调用

    Example:
        >>> # 初始化数据库
        >>> db = Sqlite3DataModule(
        ...     workdir='./data',
        ...     db_name='my_database',
        ...     tables=[
        ...         TableConfig(
        ...             name='users',
        ...             columns={'id': 'INTEGER', 'name': 'TEXT', 'email': 'TEXT'},
        ...             primary_key='id'
        ...         )
        ...     ]
        ... )
        >>>
        >>> # 插入数据
        >>> db.users.insert({'name': 'Alice', 'email': 'alice@example.com'})
        >>>
        >>> # 查询数据
        >>> result = db.users.select(where={'name': 'Alice'})
        >>> for row in result:
        ...     print(row['email'])
        >>>
        >>> # 更新数据
        >>> db.users.update({'email': 'new@example.com'}, where={'name': 'Alice'})
        >>>
        >>> # 删除数据
        >>> db.users.delete(where={'name': 'Alice'})
    """

    def __init__(self,
                 workdir: str,
                 db_name: str,
                 tables: Optional[List[TableConfig]] = None,
                 auto_connect: bool = True):
        """初始化数据库模块

        Args:
            workdir: 数据库工作目录
            db_name: 数据库名称（不包含 .db 后缀）
            tables: 表配置列表
            auto_connect: 是否自动连接数据库
        """
        self._workdir = Path(workdir)
        self._db_name = db_name if db_name.endswith('.db') else f"{db_name}.db"
        self._db_path = self._workdir / self._db_name
        self._conn: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None
        self._tables: Dict[str, TableConfig] = {}
        self._table_accessors: Dict[str, TableAccessor] = {}

        # 确保工作目录存在
        self._workdir.mkdir(parents=True, exist_ok=True)

        # 注册表配置
        if tables:
            for table in tables:
                self.register_table(table)

        # 自动连接
        if auto_connect:
            self.connect()
            self._initialize_tables()

        logger.info(f"数据库模块初始化完成: {self._db_path}")

    def __getattr__(self, name: str) -> TableAccessor:
        """通过属性访问表

        Example:
            >>> db.users.select()  # 访问 users 表
        """
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        if name in self._table_accessors:
            return self._table_accessors[name]

        if name in self._tables:
            accessor = TableAccessor(self, name)
            self._table_accessors[name] = accessor
            return accessor

        raise AttributeError(f"表 '{name}' 未注册")

    def register_table(self, table_config: TableConfig):
        """注册表配置

        Args:
            table_config: 表配置对象
        """
        self._tables[table_config.name] = table_config
        logger.info(f"注册表配置: {table_config.name}")

    def connect(self):
        """连接数据库"""
        if self._conn is not None:
            logger.warning("数据库已连接，无需重复连接")
            return

        try:
            self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row  # 支持按列名访问
            self._cursor = self._conn.cursor()
            logger.info(f"成功连接数据库: {self._db_path}")
        except Exception as e:
            logger.error(f"连接数据库失败: {e}")
            raise

    def disconnect(self):
        """断开数据库连接"""
        if self._conn:
            try:
                self._conn.commit()
                self._conn.close()
                self._conn = None
                self._cursor = None
                logger.info("数据库连接已断开")
            except Exception as e:
                logger.error(f"断开数据库连接失败: {e}")
                raise

    def _ensure_connection(self):
        """确保数据库已连接"""
        if self._conn is None:
            raise RuntimeError("数据库未连接，请先调用 connect() 方法")

    def _initialize_tables(self):
        """初始化所有已注册的表"""
        self._ensure_connection()

        for table_config in self._tables.values():
            try:
                create_sql = table_config.get_create_sql()
                self._cursor.execute(create_sql)
                logger.info(f"初始化表: {table_config.name}")
            except Exception as e:
                logger.error(f"初始化表 {table_config.name} 失败: {e}")
                raise

        self._conn.commit()

    def execute(self, sql: str, params: Optional[Tuple] = None) -> sqlite3.Cursor:
        """执行 SQL 语句

        Args:
            sql: SQL 语句
            params: 参数元组

        Returns:
            游标对象
        """
        self._ensure_connection()

        try:
            if params:
                cursor = self._cursor.execute(sql, params)
            else:
                cursor = self._cursor.execute(sql)
            self._conn.commit()
            return cursor
        except Exception as e:
            logger.error(f"执行 SQL 失败: {sql}, 错误: {e}")
            self._conn.rollback()
            raise

    def executemany(self, sql: str, params_list: List[Tuple]) -> sqlite3.Cursor:
        """批量执行 SQL 语句

        Args:
            sql: SQL 语句
            params_list: 参数元组列表

        Returns:
            游标对象
        """
        self._ensure_connection()

        try:
            cursor = self._cursor.executemany(sql, params_list)
            self._conn.commit()
            return cursor
        except Exception as e:
            logger.error(f"批量执行 SQL 失败: {sql}, 错误: {e}")
            self._conn.rollback()
            raise

    def insert(self, table: str, data: Dict[str, Any], ignore_conflict: bool = False) -> int:
        """插入数据

        Args:
            table: 表名
            data: 要插入的数据字典
            ignore_conflict: 是否忽略冲突

        Returns:
            插入行的 ID
        """
        with _write_lock:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])

            if ignore_conflict:
                sql = f"INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})"
            else:
                sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            cursor = self.execute(sql, tuple(data.values()))
            return cursor.lastrowid

    def insert_many(self, table: str, data_list: List[Dict[str, Any]], ignore_conflict: bool = False) -> int:
        """批量插入数据

        Args:
            table: 表名
            data_list: 要插入的数据字典列表
            ignore_conflict: 是否忽略冲突

        Returns:
            插入的行数
        """
        with _write_lock:
            if not data_list:
                return 0

            columns = ', '.join(data_list[0].keys())
            placeholders = ', '.join(['?' for _ in data_list[0]])

            if ignore_conflict:
                sql = f"INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})"
            else:
                sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            params_list = [tuple(data.values()) for data in data_list]
            cursor = self.executemany(sql, params_list)
            return cursor.rowcount

    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """更新数据

        Args:
            table: 表名
            data: 要更新的数据字典
            where: 条件字典

        Returns:
            影响的行数
        """
        with _write_lock:
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])

            sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            params = tuple(list(data.values()) + list(where.values()))

            cursor = self.execute(sql, params)
            return cursor.rowcount

    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """删除数据

        Args:
            table: 表名
            where: 条件字典

        Returns:
            删除的行数
        """
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        sql = f"DELETE FROM {table} WHERE {where_clause}"

        cursor = self.execute(sql, tuple(where.values()))
        return cursor.rowcount

    def select(self,
               table: str,
               columns: Optional[List[str]] = None,
               where: Optional[Dict[str, Any]] = None,
               order_by: Optional[str] = None,
               limit: Optional[int] = None,
               offset: Optional[int] = None) -> QueryResult:
        """查询数据

        Args:
            table: 表名
            columns: 要查询的列名列表
            where: 条件字典
            order_by: 排序字段
            limit: 限制返回行数
            offset: 偏移量

        Returns:
            QueryResult 对象
        """
        # 构建 SELECT 子句
        if columns:
            select_clause = ', '.join(columns)
        else:
            select_clause = '*'

        sql = f"SELECT {select_clause} FROM {table}"
        params = []

        # 构建 WHERE 子句
        if where:
            where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
            sql += f" WHERE {where_clause}"
            params.extend(where.values())

        # 构建 ORDER BY 子句
        if order_by:
            sql += f" ORDER BY {order_by}"

        # 构建 LIMIT 子句
        if limit is not None:
            sql += f" LIMIT {limit}"

        # 构建 OFFSET 子句
        if offset is not None:
            sql += f" OFFSET {offset}"

        cursor = self.execute(sql, tuple(params) if params else None)
        rows = cursor.fetchall()

        # 获取列名
        if columns:
            result_columns = columns
        else:
            result_columns = [desc[0] for desc in cursor.description]

        return QueryResult(columns=result_columns, rows=[tuple(row) for row in rows])

    def count(self, table: str, where: Optional[Dict[str, Any]] = None) -> int:
        """统计行数

        Args:
            table: 表名
            where: 条件字典

        Returns:
            符合条件的行数
        """
        sql = f"SELECT COUNT(*) FROM {table}"
        params = []

        if where:
            where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
            sql += f" WHERE {where_clause}"
            params.extend(where.values())

        cursor = self.execute(sql, tuple(params) if params else None)
        return cursor.fetchone()[0]

    def drop_table(self, table: str):
        """删除表

        Args:
            table: 表名
        """
        sql = f"DROP TABLE IF EXISTS {table}"
        self.execute(sql)
        logger.info(f"删除表: {table}")

    def drop_database(self):
        """删除数据库文件"""
        self.disconnect()

        if self._db_path.exists():
            try:
                os.remove(self._db_path)
                logger.info(f"数据库文件已删除: {self._db_path}")
            except Exception as e:
                logger.error(f"删除数据库文件失败: {e}")
                raise

    def vacuum(self):
        """优化数据库（回收空间）"""
        self.execute("VACUUM")
        logger.info("数据库优化完成")

    def get_table_names(self) -> List[str]:
        """获取所有表名

        Returns:
            表名列表
        """
        cursor = self.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cursor.fetchall()]

    def table_exists(self, table: str) -> bool:
        """检查表是否存在

        Args:
            table: 表名

        Returns:
            是否存在
        """
        return table in self.get_table_names()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.disconnect()

    def __repr__(self) -> str:
        status = "connected" if self._conn else "disconnected"
        return f"<Sqlite3DataModule(db='{self._db_path}', status='{status}', tables={list(self._tables.keys())})>"
