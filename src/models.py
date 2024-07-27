from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import Field, Relationship, SQLModel, select


class AuthorBase(SQLModel):
    name: str


class Author(AuthorBase, table=True):  # type: ignore
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
    id: int
    name: str | None = None


class BookBase(SQLModel):
    name: str
    author_id: int | None = Field(default=None, foreign_key="author.id")


class Book(BookBase, table=True):  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    author: Author | None = Relationship(back_populates="books")


class BookAdd(BookBase):
    author_id: int


class BookGet(BookAdd):
    id: int


class BookGetWithAuthor(BookGet):
    author: AuthorGet | None = None


class BookUpdate(SQLModel):
    id: int
    name: str | None = None
    author_id: int | None = None


engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3", echo=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncSession(engine) as session:
        authors = await session.scalars(select(Author))
        if not authors.first():
            author1 = Author(id=None, name="夏目漱石")
            author2 = Author(id=None, name="泉鏡花")
            book1 = Book(id=None, name="坊っちゃん", author=author1)
            book2 = Book(id=None, name="高野聖", author=author2)
            session.add_all([author1, author2, book1, book2])
            await session.commit()


async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session
