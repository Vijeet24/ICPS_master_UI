from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Product, Subcategory
from app.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    SubcategoryCreate,
    SubcategoryResponse,
    SubcategoryUpdate,
)

router = APIRouter(prefix="/api", tags=["categories"])


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()


@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A category with this name already exists",
        )
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    data = payload.model_dump(exclude_unset=True)
    if "name" in data:
        duplicate = (
            db.query(Category)
            .filter(Category.name == data["name"], Category.id != category_id)
            .first()
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A category with this name already exists",
            )

    for key, value in data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    product_count = db.query(Product).filter(Product.category_id == category_id).count()
    if product_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete category: {product_count} product(s) reference it",
        )

    db.delete(category)
    db.commit()


@router.get("/subcategories", response_model=list[SubcategoryResponse])
def list_subcategories(
    category_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Subcategory)
    if category_id is not None:
        query = query.filter(Subcategory.category_id == category_id)
    return query.order_by(Subcategory.name).all()


@router.get("/subcategories/{subcategory_id}", response_model=SubcategoryResponse)
def get_subcategory(subcategory_id: int, db: Session = Depends(get_db)):
    subcategory = db.query(Subcategory).filter(Subcategory.id == subcategory_id).first()
    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subcategory not found"
        )
    return subcategory


@router.post(
    "/subcategories", response_model=SubcategoryResponse, status_code=status.HTTP_201_CREATED
)
def create_subcategory(payload: SubcategoryCreate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == payload.category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    existing = (
        db.query(Subcategory)
        .filter(
            Subcategory.name == payload.name,
            Subcategory.category_id == payload.category_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A subcategory with this name already exists for the category",
        )

    subcategory = Subcategory(**payload.model_dump())
    db.add(subcategory)
    db.commit()
    db.refresh(subcategory)
    return subcategory


@router.put("/subcategories/{subcategory_id}", response_model=SubcategoryResponse)
def update_subcategory(
    subcategory_id: int, payload: SubcategoryUpdate, db: Session = Depends(get_db)
):
    subcategory = db.query(Subcategory).filter(Subcategory.id == subcategory_id).first()
    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subcategory not found"
        )

    data = payload.model_dump(exclude_unset=True)
    target_category_id = data.get("category_id", subcategory.category_id)
    target_name = data.get("name", subcategory.name)

    if "category_id" in data:
        category = db.query(Category).filter(Category.id == target_category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    duplicate = (
        db.query(Subcategory)
        .filter(
            Subcategory.name == target_name,
            Subcategory.category_id == target_category_id,
            Subcategory.id != subcategory_id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A subcategory with this name already exists for the category",
        )

    for key, value in data.items():
        setattr(subcategory, key, value)
    db.commit()
    db.refresh(subcategory)
    return subcategory


@router.delete("/subcategories/{subcategory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subcategory(subcategory_id: int, db: Session = Depends(get_db)):
    subcategory = db.query(Subcategory).filter(Subcategory.id == subcategory_id).first()
    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subcategory not found"
        )

    product_count = db.query(Product).filter(Product.sub_category_id == subcategory_id).count()
    if product_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete subcategory: {product_count} product(s) reference it",
        )

    db.delete(subcategory)
    db.commit()
