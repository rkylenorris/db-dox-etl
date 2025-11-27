from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from .utils import LogLevel, Environment, SqlType, CONNECTION_TEMPLATES


class DBCredentials(BaseModel):
    user: str
    password: str

    def __str__(self) -> str:
        return f"{self.user}:{self.password}"


class DbSettings(BaseModel):
    db_type: SqlType
    host: str  # server address
    port: int | None = None  # optional port
    database: str  # database name or file path for sqlite
    credentials: DBCredentials
    driver: str | None = None  # optional driver for some DBs

    @property
    def connection_string(self) -> str:
        if self.db_type == SqlType.SQLITE_MEMORY:
            template = CONNECTION_TEMPLATES["sqlite_memory"]
            return template
        elif self.db_type == SqlType.SQLITE:
            template = CONNECTION_TEMPLATES["sqlite"]
            return template.format(
                path_to_file=self.database
            )
        elif self.db_type == SqlType.SQLSERVER:
            if self.port:
                template = CONNECTION_TEMPLATES["mssql"]["port"]
            else:
                template = CONNECTION_TEMPLATES["mssql"]["no_port"]
            return template.format(
                user=self.credentials.user,
                password=self.credentials.password,
                host=self.host,
                port=self.port if self.port else "",
                database=self.database,
                driver=self.driver if self.driver else "ODBC+Driver+17+for+SQL+Server"
            )
        else:
            template = CONNECTION_TEMPLATES.get(self.db_type.value)
            if template is None:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            return template.format(
                user=self.credentials.user,
                password=self.credentials.password,
                host=self.host,
                port=self.port if self.port else "",
                database=self.database
            )
