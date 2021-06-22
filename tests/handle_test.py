from dataclasses import dataclass, field
from strawberry_crud import SqlalchemyCRUD
from sqlalchemy import Column, String, Integer, Table, select
import strawberry
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import registry
import asyncio


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

@dataclass
class User:
    id: int = field(init=False)
    username: str
    password: str

mapper_registry.map_imperatively(User, user_table)

async def create():
    async with engine.begin() as conn:
        await conn.run_sync(user_table.metadata.create_all)

asyncio.run(create())

crud_graph = SqlalchemyCRUD(get_db=get_session, cls=User, db_model=user_table)

@strawberry.type
class Query(crud_graph.query()):pass

@strawberry.type
class Mutation(crud_graph.mutation()):pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
