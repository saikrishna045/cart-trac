from fastapi import Depends, FastAPI
from models import Product
from db import SessionLocal, Base, engine
import db_models
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def greet():
    return {"message": "hello"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    db_products = db.query(db_models.Product).all()
    return db_products


@app.get("/products/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    db_product = db.query(db_models.Product).filter(
        db_models.Product.id == id
    ).first()

    if db_product:
        return db_product

    return "product not found"


@app.post("/products")
def add_product(product: Product, db: Session = Depends(get_db)):
    new_product = db_models.Product(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@app.put("/products")
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    db_product = db.query(db_models.Product).filter(
        db_models.Product.id == id
    ).first()

    if db_product:
        db_product.name = product.name
        db_product.description = product.description
        db_product.quantity = product.quantity
        db_product.price = product.price

        db.commit()
        db.refresh(db_product)

        return db_product

    return "product not found"


@app.delete("/products")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(db_models.Product).filter(
        db_models.Product.id == id
    ).first()

    if db_product:
        db.delete(db_product)
        db.commit()

        return "deleted successfully"

    return "product not found"