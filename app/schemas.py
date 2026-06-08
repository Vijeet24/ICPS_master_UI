from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BrandBase(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=255)
    brand_gln: Optional[str] = Field(None, max_length=13)
    company_prefix: Optional[str] = Field(None, max_length=12)
    address: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    brand_name: Optional[str] = Field(None, min_length=1, max_length=255)
    brand_gln: Optional[str] = Field(None, max_length=13)
    company_prefix: Optional[str] = Field(None, max_length=12)
    address: Optional[str] = None


class BrandResponse(BrandBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class SubcategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category_id: int


class SubcategoryCreate(SubcategoryBase):
    pass


class SubcategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category_id: Optional[int] = None


class SubcategoryResponse(SubcategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ProductBase(BaseModel):
    gtin_14: str = Field(..., min_length=14, max_length=14)
    product_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    unit_of_measure: str = Field(..., min_length=1, max_length=50)
    default_price: Optional[Decimal] = Field(None, ge=0)
    currency: str = Field(..., min_length=3, max_length=3)
    brand_id: int
    gs1_digital_link: Optional[str] = Field(None, max_length=512)

    @field_validator("gtin_14")
    @classmethod
    def validate_gtin(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("GTIN-14 must contain only digits")
        return value

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        normalized = value.upper()
        if not normalized.isalpha() or len(normalized) != 3:
            raise ValueError("Currency must be a 3-letter ISO code")
        return normalized


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    gtin_14: Optional[str] = Field(None, min_length=14, max_length=14)
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    unit_of_measure: Optional[str] = Field(None, min_length=1, max_length=50)
    default_price: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    brand_id: Optional[int] = None
    gs1_digital_link: Optional[str] = Field(None, max_length=512)

    @field_validator("gtin_14")
    @classmethod
    def validate_gtin(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.isdigit():
            raise ValueError("GTIN-14 must contain only digits")
        return value

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.upper()
        if not normalized.isalpha() or len(normalized) != 3:
            raise ValueError("Currency must be a 3-letter ISO code")
        return normalized


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand_name: str
    category_name: Optional[str] = None
    sub_category_name: Optional[str] = None
    category_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
