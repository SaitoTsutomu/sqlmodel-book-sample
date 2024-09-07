import pytest


@pytest.mark.asyncio
class TestAuthors:
    URL = "/authors"

    async def test_post(self, client, author1_data):
        author = (await client.post(self.URL, json=author1_data)).json()
        assert author == author1_data | {"id": author["id"]}

    async def test_get_all(self, client, author1, author2):
        authors = (await client.get(self.URL)).json()
        assert authors == [author1, author2]

    async def test_get_one(self, client, author1):
        author = (await client.get(f"{self.URL}/{author1['id']}")).json()
        assert author == author1

    async def test_get_details(self, client, author1, book1):
        author = (await client.get(f"{self.URL}/{author1['id']}/details")).json()
        assert author == author1 | {"books": [book1]}

    async def test_patch_name(self, client, author1):
        data = {"id": author1["id"], "name": "NewName"}
        author = (await client.patch(self.URL, json=data)).json()
        assert author == data

    async def test_delete(self, client, author1, author2, book1):
        await client.delete(f"{self.URL}?author_id={author1['id']}")
        authors = (await client.get(self.URL)).json()
        assert len(authors) == 1
        books = (await client.get("/books")).json()
        assert len(books) == 0


@pytest.mark.asyncio
class TestBooks:
    URL = "/books"

    async def test_post(self, client, book1_data):
        book = (await client.post(self.URL, json=book1_data)).json()
        assert book == book1_data | {"id": book["id"]}

    async def test_get_all(self, client, book1):
        books = (await client.get(self.URL)).json()
        assert books == [book1]

    async def test_get_one(self, client, book1):
        book = (await client.get(f"{self.URL}/{book1['id']}")).json()
        assert book == book1

    async def test_get_details(self, client, author1, book1):
        book = (await client.get(f"{self.URL}/{book1['id']}/details")).json()
        assert book == book1 | {"author": author1}

    async def test_patch_name(self, client, book1):
        data = {"id": book1["id"], "name": "NewName"}
        book = (await client.patch(self.URL, json=data)).json()
        assert book == data | {"author_id": book1["author_id"]}

    async def test_patch_author(self, client, author2, book1):
        data = {"id": book1["id"], "author_id": author2["id"]}
        book = (await client.patch(self.URL, json=data)).json()
        assert book == data | {"name": book1["name"]}

    async def test_delete(self, client, book1):
        await client.delete(f"{self.URL}?book_id={book1['id']}")
        books = (await client.get(f"{self.URL}")).json()
        assert len(books) == 0
