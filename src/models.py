from typing import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Field, Relationship, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession


class AuthorBase(SQLModel):
    name: str


class Author(AuthorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    books: list["Book"] = Relationship(
        back_populates="author", sa_relationship_kwargs={"cascade": "delete"}
    )


class AuthorAdd(AuthorBase):
    pass


class AuthorGet(AuthorAdd):
    id: int


class AuthorGetWithBooks(AuthorGet):
    books: list["BookGet"] = Field(default_factory=list)


class AuthorUpdate(SQLModel):
    name: str | None = None


class BookBase(SQLModel):
    name: str
    author_id: int | None = Field(default=None, foreign_key="author.id")


class Book(BookBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    author: Author | None = Relationship(back_populates="books")


class BookAdd(BookBase):
    author_id: int


class BookGet(BookAdd):
    id: int


class BookGetWithAuthor(BookGet):
    author: AuthorGet | None = None


class BookUpdate(SQLModel):
    name: str | None = None
    author_id: int | None = None


engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3", echo=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncSession(engine) as session:
        authors = await session.scalars(select(Author))
        if not authors.first():
            author = Author(id=None, name="夏目漱石")
            book = Book(id=None, name="坊っちゃん", author_id=author.id, author=author)
            session.add_all([author, book])
            await session.commit()


async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session
