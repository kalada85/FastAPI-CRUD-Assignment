from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Optional
app = FastAPI(title="Bookstore APP")


# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = "sqlite:///./bookstore.db"

engine = create_engine(
    DATABASE_URL,
connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# DATABASE MODEL
# ============================================================

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    in_stock = Column(Boolean, default=True)
    published_year = Column(Integer, nullable=True)


    # Create the database tables
Base.metadata.create_all(bind=engine)


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# PYDANTIC SCHEMAS
# ============================================================

class BookCreate(BaseModel):
    title: str
    author: str
    passrice: float
    category: str
    in_stock: bool = True
    published_year: Optional[int] = None


class BookUpdate(BaseModel):
    title: str
    author: str
    price: float
    category: str
    in_stock: bool
    published_year: Optional[int] = None


class BookPatch(BaseModel):
    in_stock: Optional[bool] = None



# HOME ENDPOINT
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Welcome to the Bookstore API"
    }


# ============================================================
# POST /books/
# ADD A NEW BOOK
# ============================================================

@app.post("/books/")
def create_book(book: BookCreate, db: Session = Depends(get_db)):

    new_book = Book(
        title=book.title,
        author=book.author,
        price=book.price,
        category=book.category,
        in_stock=book.in_stock,
        published_year=book.published_year
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book



# GET /books/
# GET ALL BOOKS
# WITH QUERY PARAMETERS
# ============================================================

@app.get("/books/")
def get_books(
    Category: Optional[str] = None,
    Published_after: Optional[int] = None,
    Max_price: Optional[float] = None,
    Sort_by: Optional[str] = None,
    Limit: int = 10,
    Skip: int = 0,
    db: Session = Depends(get_db)
):

    Query = db.query(Book)

    # Filter by category
    if category:
        Query = query.filter(Book.category == category)

    # Filter by published year
    if published_after:
        Query = query.filter(Book.published_year > published_after)

    # Filter by maximum price
    if max_price is not None:
        Query = query.filter(Book.price <= max_price)

    # Sort results
    if sort_by == "price":
        Query = query.order_by(Book.price)

    elif sort_by == "-price":
        Query = query.order_by(Book.price.desc())

    elif sort_by == "title":
        Query = query.order_by(Book.title)

    elif sort_by == "-title":
        Query = query.order_by(Book.title.desc())

    elif sort_by == "published_year":
        Query = query.order_by(Book.published_year)

    elif sort_by == "-published_year":
        Query = query.order_by(Book.published_year.desc())

    # Pagination
    Books = query.offset(skip).limit(limit).all()

    return books


# GET /books/{book_id}
# GET BOOK BY ID
# ============================================================

@app.get("/books/{book_id}")
def get_book(
    Book_id: int,
    db: Session = Depends(get_db)
):

    Book = db.query(Book).filter(Book.id == book_id).first()

    if book is None:
        raise HTTPException(
            Status_code=404,
            Detail="Book not found"
        )

    return book


# ============================================================
# GET /categories/
# LIST ALL CATEGORIES
# ============================================================

@app.get("/categories/")
def get_categories(
    db: Session = Depends(get_db)
):

    Categories = db.query(Book.category).distinct().all()

    return [
        category[0]
        for category in categories
    ]


# GET /categories/{category}
# GET BOOKS BY CATEGORY
# ============================================================

@app.get("/categories/{category}")
def get_books_by_category(
    Category: str,
    db: Session = Depends(get_db)
):

    Books = db.query(Book).filter(
        Book.category == category
    ).all()

    return books


# ============================================================
# PUT /books/{book_id}
# UPDATE ENTIRE BOOK
# ============================================================

@app.put("/books/{book_id}")
def update_book(
    Book_id: int,
    Book_data: BookUpdate,
    db: Session = Depends(get_db)
):

    Book = db.query(Book).filter(
        Book.id == book_id
    ).first()

    if book is None:
        raise HTTPException(
            Status_code=404,
            Detail="Book not found"
        )

    Book.title = book_data.title
    Book.author = book_data.author
    Book.price = book_data.price
    Book.category = book_data.category
    Book.in_stock = book_data.in_stock
    Book.published_year = book_data.published_year

    db.commit()
    db.refresh(book)

    return book



# PATCH /books/{book_id}
# UPDATE SPECIFIC FIELD
# ============================================================

@app.patch("/books/{book_id}")
def patch_book(
    Book_id: int,
    Book_data: BookPatch,
    db: Session = Depends(get_db)
):

    Book = db.query(Book).filter(
        Book.id == book_id
    ).first()

    if book is None:
        raise HTTPException(
            Status_code=404,
            Detail="book not found"
        )

    if book_data.in_stock is not None:
        Book.in_stock = book_data.in_stock

    db.commit()
    db.refresh(book)

    return book


# ============================================================
# DELETE /books/{book_id}
# DELETE A BOOK
# ============================================================

@app.delete("/books/{book_id}")
def delete_book(
    Book_id: int,
    db: Session = Depends(get_db)
):

    Book = db.query(Book).filter(
        Book.id == book_id
    ).first()

    if book is None:
        raise HTTPException(
            Status_code=404,
            Detail="Book not found"
        )

    db.delete(book)
    db.commit()

    return {
        "message": "Book deleted successfully"
    }
