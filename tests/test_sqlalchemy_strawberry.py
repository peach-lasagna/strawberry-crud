from sqlalchemy import Column, String, Integer, Table, select
from sqlalchemy.orm import sessionmaker, registry
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from dataclasses import field
from strawberry_crud import SqlalchemyCRUD
import unittest
import strawberry


class StrawberryAlchemyTest(unittest.IsolatedAsyncioTestCase):
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

    crud = SqlalchemyCRUD(schema=User, get_db=get_session)
    
    @strawberry.type
    class Query(crud.query()):
        @strawberry.field
        async def field_to_test(self) -> str:
            return "query"

    @strawberry.type
    class Mutation(crud.mutation()):
        @strawberry.field
        async def field_to_test(self) -> str:
            return "mutation"

    async def assertQueryResult(self, query: str, expected_res: dict):
        found_res = await self.execute(query)
        self.assertEqual(expected_res, found_res.data)

    async def asyncSetUp(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.user_table.metadata.create_all)

    def setUp(self):
        self.schema = strawberry.Schema(query=self.Query, mutation=self.Mutation)
        self.execute = self.schema.execute

    async def asyncTearDown(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.user_table.metadata.drop_all)

    async def test_create(self):
        # query = 
        await self.("{ createUser() }")
