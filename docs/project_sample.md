# Add and Review Items in Shopping Cart

> [Priority: High]

## User Story
As an e-commerce customer, I want to add items to my shopping cart and view the total price, so that I can review my order before checkout.

## Acceptance Criteria

### AC-01: Add Item to Cart
**Given** a user is logged in and views a product  
**When** the user clicks the "Add to Cart" button for a product  
**Then** the product is added to the shopping cart  
**And** the user sees a confirmation message "Item added to cart."

### AC-02: View Cart with Total Price
**Given** a user has added items to their shopping cart  
**When** the user navigates to the shopping cart page  
**Then** the user sees all items listed in the cart  
**And** each item displays its price  
**And** the total price of all items is displayed at the bottom of the list

### AC-03: Add Item to Cart Without Stock
**Given** a user is logged in and views a product with zero stock  
**When** the user attempts to add the product to the cart  
**Then** the product is not added to the shopping cart  
**And** the user sees an error message "This item is out of stock."

## Technical Contract

### Request: Add Item to Cart
```json
POST /api/cart/add
{
  "userId": "string",
  "productId": "string",
  "quantity": "integer"
}
```

### Response: Add Item to Cart
```json
200 OK
{
  "message": "Item added to cart."
}
```

```json
400 Bad Request
{
  "error": "This item is out of stock."
}
```

### Request: View Cart
```json
GET /api/cart
{
  "userId": "string"
}
```

### Response: View Cart
```json
200 OK
{
  "items": [
    {
      "productId": "string",
      "name": "string",
      "price": "float",
      "quantity": "integer"
    }
  ],
  "totalPrice": "float"
}
```