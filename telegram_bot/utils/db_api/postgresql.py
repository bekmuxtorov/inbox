from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        telegram_id BIGINT NOT NULL UNIQUE,
        full_name VARCHAR(255) NOT NULL,
        phone_number varchar(255) NULL, 
        username varchar(255) NULL,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, telegram_id, full_name, phone_number, username):
        sql = "INSERT INTO users (telegram_id, full_name, phone_number, username) VALUES($1, $2, $3, $4) returning *"
        data = await self.execute(sql, telegram_id, full_name, phone_number, username, fetchrow=True)
        return {
            "telegram_id": data[0],
            "full_name": data[1],
            "phone_number": data[2],
            "username": data[3],
            "created_at": data[4],
        } if data else None

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        data = await self.execute(sql, fetch=True)
        return [
            {
                "telegram_id": item[0],
                "full_name": item[1],
                "phone_number": item[2],
                "username": item[3],
                "created_at": item[4],
            }
            for item in data
        ] if data else None

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        data = await self.execute(sql, *parameters, fetchrow=True)
        return {
            "telegram_id": data[0],
            "full_name": data[1],
            "phone_number": data[2],
            "username": data[3],
            "created_at": data[4],
        } if data else None

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)
