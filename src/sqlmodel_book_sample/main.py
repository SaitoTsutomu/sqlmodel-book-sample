from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import (
    Author,
    AuthorAdd,
    AuthorGet,
    AuthorGetWithBooks,
    AuthorUpdate,
    Book,
    BookAdd,
    BookGet,
    BookGetWithAuthor,
    BookUpdate,
    get_db,
    init_db,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()  # setup
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/authors", tags=["/authors"])
async def add_author(author: AuthorAdd, db: Annotated[AsyncSession, Depends(get_db)]) -> AuthorGet:
    author_new = Author.model_validate(author)
    db.add(author_new)
    await db.commit()
    await db.refresh(author_new)
    return author_new


@app.post("/books", tags=["/books"])
async def add_book(book: BookAdd, db: Annotated[AsyncSession, Depends(get_db)]) -> BookGet:
    author = await db.get(Author, book.author_id)
    if not author:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown author_id")
    book_new = Book.model_validate(book)
    db.add(book_new)
    await db.commit()
    await db.refresh(book_new)
    return book_new


@app.get("/authors", tags=["/authors"])
async def get_authors(db: Annotated[AsyncSession, Depends(get_db)]) -> list[AuthorGet]:
    return await db.scalars(select(Author))


@app.get("/books", tags=["/books"])
async def get_books(db: Annotated[AsyncSession, Depends(get_db)]) -> list[BookGet]:
    return await db.scalars(select(Book))


@app.get("/authors/{author_id}", tags=["/authors"])
async def get_author(author_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> AuthorGet:
    author = await db.get(Author, author_id)
    if not author:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown author_id")
    return author


@app.get("/books/{book_id}", tags=["/books"])
async def get_book(book_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> BookGet:
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown book_id")
    return book


@app.get("/authors/{author_id}/details", tags=["/authors"])
async def author_details(author_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> AuthorGetWithBooks:
    q = select(Author).where(Author.id == author_id)
    author = await db.scalar(q.options(selectinload(Author.books)))
    if not author:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown author_id")
    return author


@app.get("/books/{book_id}/details", tags=["/books"])
async def book_details(book_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> BookGetWithAuthor:
    book = await db.scalar(
        select(Book).where(Book.id == book_id).options(selectinload(Book.author)),
    )
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown book_id")
    return book


@app.patch("/authors", tags=["/authors"])
async def update_author(author: AuthorUpdate, db: Annotated[AsyncSession, Depends(get_db)]) -> AuthorGet:
    author_cur = await db.get(Author, author.id)
    if not author_cur:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown author.id")
    if author.name is not None:
        author_cur.name = author.name
    await db.commit()
    await db.refresh(author_cur)
    return author_cur


@app.patch("/books", tags=["/books"])
async def update_book(book: BookUpdate, db: Annotated[AsyncSession, Depends(get_db)]) -> BookGet:
    book_cur = await db.get(Book, book.id)
    if not book_cur:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown book.id")
    if book.name is not None:
        book_cur.name = book.name
    if book.author_id is not None:
        author_cur = await db.get(Author, book.author_id)
        if not author_cur:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown book.author_id")
        book_cur.author = author_cur
    await db.commit()
    await db.refresh(book_cur)
    return book_cur


@app.delete("/authors", tags=["/authors"])
async def delete_author(author_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    author = await db.get(Author, author_id)
    if author is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown author_id")
    await db.delete(author)
    await db.commit()


@app.delete("/books", tags=["/books"])
async def delete_book(book_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    book = await db.get(Book, book_id)
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown book_id")
    await db.delete(book)
    await db.commit()
