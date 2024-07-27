from contextlib import asynccontextmanager

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
async def lifespan(app: FastAPI):
    await init_db()  # setup
    yield
    pass  # teardown


app = FastAPI(lifespan=lifespan)


@app.post("/authors", tags=["/authors"])
async def add_author(author: AuthorAdd, db: AsyncSession = Depends(get_db)) -> AuthorGet:
    author_new = Author.model_validate(author)
    db.add(author_new)
    await db.commit()
    await db.refresh(author_new)
    return AuthorGet.model_validate(author_new)


@app.post("/books", tags=["/books"])
async def add_book(book: BookAdd, db: AsyncSession = Depends(get_db)) -> BookGet:
    author = await db.get(Author, book.author_id)
    if not author:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown author_id")
    book_new = Book.model_validate(book)
    db.add(book_new)
    await db.commit()
    await db.refresh(book_new)
    return BookGet.model_validate(book_new)


@app.get("/authors", tags=["/authors"])
async def get_authors(db: AsyncSession = Depends(get_db)) -> list[AuthorGet]:
    return list(map(AuthorGet.model_validate, await db.exec(select(Author))))


@app.get("/books", tags=["/books"])
async def get_books(db: AsyncSession = Depends(get_db)) -> list[BookGet]:
    return list(map(BookGet.model_validate, await db.exec(select(Book))))


@app.get("/authors/{author_id}", tags=["/authors"])
async def get_author(author_id: int, db: AsyncSession = Depends(get_db)) -> AuthorGet:
    author = await db.get(Author, author_id)
    if not author:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown author_id")
    return AuthorGet.model_validate(author)


@app.get("/books/{book_id}", tags=["/books"])
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)) -> BookGet:
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown book_id")
    return BookGet.model_validate(book)


@app.get("/authors/{author_id}/details", tags=["/authors"])
async def author_details(author_id: int, db: AsyncSession = Depends(get_db)) -> AuthorGetWithBooks:
    q = select(Author).where(Author.id == author_id)
    author = await db.scalar(q.options(selectinload(Author.books)))  # type: ignore
    if not author:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown author_id")
    return AuthorGetWithBooks.model_validate(author)


@app.get("/books/{book_id}/details", tags=["/books"])
async def book_details(book_id: int, db: AsyncSession = Depends(get_db)) -> BookGetWithAuthor:
    book = await db.scalar(
        select(Book).where(Book.id == book_id).options(selectinload(Book.author))  # type: ignore
    )
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown book_id")
    return BookGetWithAuthor.model_validate(book)


@app.patch("/authors", tags=["/authors"])
async def update_author(author: AuthorUpdate, db: AsyncSession = Depends(get_db)) -> AuthorGet:
    author_cur = await db.get(Author, author.id)
    if not author_cur:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown author.id")
    if author.name is not None:
        author_cur.name = author.name
    db.add(author_cur)
    await db.commit()
    await db.refresh(author_cur)
    return AuthorGet.model_validate(author_cur)


@app.patch("/books", tags=["/books"])
async def update_book(book: BookUpdate, db: AsyncSession = Depends(get_db)) -> BookGet:
    book_cur = await db.get(Book, book.id)
    if not book_cur:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown book.id")
    if book.author_id is not None:
        author = await db.get(Author, book.author_id)
        if not author:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown book.author_id")
    if book.name is not None:
        book_cur.name = book.name
    if book.author_id is not None:
        book_cur.author_id = book.author_id
    db.add(book_cur)
    await db.commit()
    await db.refresh(book_cur)
    return BookGet.model_validate(book_cur)


@app.delete("/authors", tags=["/authors"])
async def delete_author(author_id: int, db: AsyncSession = Depends(get_db)) -> None:
    author = await db.get(Author, author_id)
    if author is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown author_id")
    await db.delete(author)
    await db.commit()


@app.delete("/books", tags=["/books"])
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)) -> None:
    book = await db.get(Book, book_id)
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown book_id")
    await db.delete(book)
    await db.commit()
