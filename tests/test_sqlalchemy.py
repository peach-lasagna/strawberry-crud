from sqlalchemy import Column, String, Integer, Table, select
import strawberry
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import registry
from dataclasses import field
from strawberry_crud import SqlalchemyCRUD
# import pytest
import unittest



class AlchemyTest(unittest.IsolatedAsyncioTestCase):
    engine = create_async_engine("sqlite+aiosqlite:///tests/test.db", pool_pre_ping=True, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, class_=AsyncSession, bind=engine)
    mapper_registry = registry()

    async def get_session(self) -> AsyncSession:
        async with self.SessionLocal() as session:
            return session

    user_table = Table(
        'users',
        mapper_registry.metadata,
        Column('id', Integer, primary_key=True, index=True, autoincrement=True),
        Column('username', String, unique=True),
        Column('password', String(128)),
    )

    @strawberry.type
    class User:
        id: int = field(init=False)
        username: str
        password: str

    mapper_registry.map_imperatively(User, user_table)

    async def asyncSetUp(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.user_table.metadata.create_all)

    def setUp(self):
        self.crud = SqlalchemyCRUD(schema=self.User, get_db=self.get_session)

    async def asyncTearDown(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.user_table.metadata.drop_all)

    async def test_create(self):
        obj = self.User(username="username", password="password") # type: ignore
        await self.crud._create(obj)
        obj.id = 1
        expected = (obj,) 
        session = await self.get_session()
        found = await session.execute(select(self.User))
        self.assertEqual( expected, found.first())
        await session.rollback()

    async def test_delete(self):
        session = await self.get_session()
        obj = self.User(username="username", password="password") # type: ignore
        session.add(obj)
        await session.commit()
        obj2 = self.User(username="username", password="password") # type: ignore
        obj2.id = 1
        found = await session.execute(select(self.User))
        expected = (obj2,) 
        self.assertEqual( expected, found.first())
        await self.crud._delete_one(item_id=1)
        self.assertEqual( (await session.execute(select(self.User))).all(), [])
        await session.rollback()
# @strawberry.type
# class Query(crud.query()):
#     pass

# @strawberry.type
# class Mutation(crud.mutation()):
#     pass

# schema = strawberry.Schema(query=Query, mutation=Mutation)
