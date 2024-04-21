import io
import os
import hashlib
import sqlite3
import traceback
from typing import Literal


class Column:
    def __init__(self, raw_column: tuple):
        raw_column = raw_column[1:]

        self.name: str = raw_column[0]
        self.type: Literal['INTEGER', 'BLOB', 'TEXT'] = raw_column[1]
        self.not_null: bool = bool(raw_column[2])
        self.default: str | None = raw_column[3]
        self.primary_key: bool = bool(raw_column[4])

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'type': self.type,
            'not_null': self.not_null,
            'default': self.default,
            'primary_key': self.primary_key
        }

    def to_string(self) -> str:
        return (
            f'{self.name} {self.type}'
            f'{" NOT NULL" if self.not_null else ""}'
            f'{f" DEFAULT {self.default}" if self.default is not None else ""}'
            f'{" PRIMARY KEY" if self.primary_key else ""}'
        )

    def __str__(self):
        return self.to_string()


class SQLiteDump:
    def __init__(self, table_name: str, columns: tuple[Column, ...]):
        self.name = table_name
        self.columns = columns

    def to_dict(self) -> dict:
        return {
            self.name: {column.name: column.to_dict() for column in self.columns}
        }

    def to_string(self) -> str:
        columns = [i.to_string() for i in self.columns]
        columns = ', '.join(columns)

        return f'CREATE TABLE {self.name}({columns})'

    def __str__(self):
        return self.to_string()


def get_sqlite_dumps(cursor: sqlite3.Cursor) -> tuple[SQLiteDump, ...]:
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    out = []

    for table in tables:
        table = table[0]
        columns_data = cursor.execute(f'PRAGMA table_info({table})').fetchall()
        ready_columns = [Column(column_unpacked) for column_unpacked in columns_data]

        out.append(SQLiteDump(table, tuple(ready_columns)))
    return tuple(out)


def format_exception(exception: BaseException) -> str:
    formatted_exception = traceback.format_exception(type(exception), exception, exception.__traceback__)
    return ''.join(formatted_exception).rstrip('\n')


def calculate_sha256(filepath: str | os.PathLike | bytes | io.BytesIO) -> str:
    sha256_hash = hashlib.sha256()

    if isinstance(filepath, (str, os.PathLike)):
        with open(filepath, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b''):
                sha256_hash.update(chunk)

    elif isinstance(filepath, (io.BytesIO, bytes)):
        sha256_hash.update(filepath)

    return sha256_hash.hexdigest()
