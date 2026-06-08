export function validateBrandForm(values) {
  const errors = {};
  if (!values.brand_name?.trim()) {
    errors.brand_name = "Brand Name is required.";
  }
  return errors;
}

export function validateCategoryForm(values) {
  const errors = {};
  if (!values.name?.trim()) {
    errors.name = "Category name is required.";
  }
  return errors;
}

export function validateSubcategoryForm(values) {
  const errors = {};
  if (!values.name?.trim()) {
    errors.name = "Subcategory name is required.";
  }
  if (!values.category_id) {
    errors.category_id = "Parent category is required.";
  }
  return errors;
}

export function validateProductForm(values) {
  const errors = {};

  if (!values.gtin_14?.trim()) {
    errors.gtin_14 = "GTIN-14 is required.";
  } else if (!/^\d{14}$/.test(values.gtin_14.trim())) {
    errors.gtin_14 = "GTIN-14 must be exactly 14 digits.";
  }

  if (!values.product_name?.trim()) {
    errors.product_name = "Product name is required.";
  }

  if (!values.unit_of_measure?.trim()) {
    errors.unit_of_measure = "Unit of measure is required.";
  }

  if (!values.currency?.trim()) {
    errors.currency = "Currency is required.";
  } else if (!/^[A-Za-z]{3}$/.test(values.currency.trim())) {
    errors.currency = "Currency must be a 3-letter ISO code.";
  }

  if (!values.brand_id) {
    errors.brand_id = "Brand Name is required.";
  }

  if (values.default_price !== "" && values.default_price != null) {
    const price = Number(values.default_price);
    if (Number.isNaN(price) || price < 0) {
      errors.default_price = "Default price must be a non-negative number.";
    }
  }

  if (values.sub_category_id && !values.category_id) {
    errors.category_id = "Select a category before choosing a subcategory.";
  }

  return errors;
}

export function isFormValid(errors) {
  return Object.keys(errors).length === 0;
}
