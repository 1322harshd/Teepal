-- Table to store users
CREATE TABLE Users (
    UserId SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Email VARCHAR(100) UNIQUE NOT NULL,
    Password VARCHAR(255),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store products
CREATE TABLE Products (
    ProductId SERIAL PRIMARY KEY,
    Item VARCHAR(100) NOT NULL,
    Brand VARCHAR(100),
    Price DECIMAL(10, 2) NOT NULL,
    Image TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store cart items (many-to-many relationship between users and products)
CREATE TABLE CartItems (
    CartItemId SERIAL PRIMARY KEY,
    UserId INTEGER REFERENCES Users(UserId) ON DELETE CASCADE,
    ProductId INTEGER REFERENCES Products(ProductId) ON DELETE CASCADE,
    Quantity INTEGER NOT NULL CHECK (Quantity > 0),
    AddedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store saved items (wishlist)
CREATE TABLE SavedItems (
    SavedItemId SERIAL PRIMARY KEY,
    UserId INTEGER REFERENCES Users(UserId) ON DELETE CASCADE,
    ProductId INTEGER REFERENCES Products(ProductId) ON DELETE CASCADE,
    SavedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store orders
CREATE TABLE Orders (
    OrderId SERIAL PRIMARY KEY,
    UserId INTEGER REFERENCES Users(UserId) ON DELETE SET NULL,
    OrderedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to link products to an order
CREATE TABLE OrderDetails (
    OrderDetailId SERIAL PRIMARY KEY,
    OrderId INTEGER REFERENCES Orders(OrderId) ON DELETE CASCADE,
    ProductId INTEGER REFERENCES Products(ProductId),
    Quantity INTEGER NOT NULL,
    PriceAtPurchase DECIMAL(10, 2)
);
