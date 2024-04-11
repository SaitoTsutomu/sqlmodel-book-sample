import pytest


@pytest.mark.asyncio
async def test_it(client):
    # 著者1を追加
    author1 = (await client.post("/authors", data='{"name": "author1"}')).json()
    assert author1 == {"id": 1, "name": "author1"}, "POST /authors"

    # 全著者を確認
    authors = (await client.get("/authors")).json()
    assert authors == [author1], "GET /authors"

    # 著者1を確認
    actual = (await client.get("/authors/1")).json()
    assert actual == author1, "GET /authors/{author_id}"

    # 著者1の詳細を確認
    actual = (await client.get("/authors/1/details")).json()
    expected = author1 | {"books": []}
    assert actual == expected, "GET /authors/{book_id}/details"

    # 著者1を更新
    actual = (await client.patch("/authors?author_id=1", data='{"name": "test1"}')).json()
    assert actual == {"id": 1, "name": "test1"}, "PATCH /authors"

    # 書籍1を追加
    book1 = (await client.post("/books", data='{"name": "book1", "author_id": 1}')).json()
    assert book1 == {"id": 1, "name": "book1", "author_id": 1}, "POST /books"

    # 書籍2を追加
    book2 = (await client.post("/books", data='{"name": "book2", "author_id": 1}')).json()
    assert book2 == {"id": 2, "name": "book2", "author_id": 1}, "POST /books"

    # 全書籍を確認
    books = (await client.get("/books")).json()
    assert books == [book1, book2], "GET /books"

    # 書籍2を確認
    actual = (await client.get("/books/2")).json()
    assert actual == book2, "GET /books/{book_id}"

    # 書籍2の詳細を確認
    actual = (await client.get("/books/2/details")).json()
    expected = book2 | {"author": {"id": 1, "name": "test1"}}
    assert actual == expected, "GET /books/{book_id}/details"

    # 書籍2を更新
    actual = (await client.patch("/books?book_id=2", data='{"name": "test2"}')).json()
    book2 |= {"name": "test2"}
    assert actual == book2, "PATCH /books"

    # 書籍1を削除して全書籍を確認
    await client.delete("/books?book_id=1")
    books = (await client.get("/books")).json()
    assert books == [book2], "DELETE /books"

    # 著者1を削除して全著者と全書籍が空を確認
    await client.delete("/authors?author_id=1")
    authors = (await client.get("/authors")).json()
    assert authors == [], "DELETE /authors"
    books = (await client.get("/books")).json()
    assert books == [], "CASCADE by DELETE /authors"
