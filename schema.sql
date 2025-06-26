BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "CartItems" (
	"CartItemId"	INTEGER,
	"UserId"	INTEGER,
	"ProductId"	INTEGER,
	"Quantity"	INTEGER NOT NULL CHECK("Quantity" > 0),
	"AddedAt"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("CartItemId" AUTOINCREMENT),
	FOREIGN KEY("ProductId") REFERENCES "Products"("ProductId") ON DELETE CASCADE,
	FOREIGN KEY("UserId") REFERENCES "Users"("UserId") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "OrderDetails" (
	"OrderDetailId"	INTEGER,
	"OrderId"	INTEGER,
	"ProductId"	INTEGER,
	"Quantity"	INTEGER NOT NULL CHECK("Quantity" > 0),
	"PriceAtPurchase"	DECIMAL(10, 2),
	PRIMARY KEY("OrderDetailId" AUTOINCREMENT),
	FOREIGN KEY("OrderId") REFERENCES "Orders"("OrderId") ON DELETE CASCADE,
	FOREIGN KEY("ProductId") REFERENCES "Products"("ProductId")
);
CREATE TABLE IF NOT EXISTS "Orders" (
	"OrderId"	INTEGER,
	"UserId"	INTEGER,
	"OrderedAt"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	"ArrivalDate"	TEXT,
	"Status"	TEXT DEFAULT 'Arriving',
	PRIMARY KEY("OrderId" AUTOINCREMENT),
	FOREIGN KEY("UserId") REFERENCES "Users"("UserId") ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS "Products" (
	"ProductId"	INTEGER,
	"Item"	VARCHAR(100) NOT NULL,
	"Brand"	VARCHAR(100),
	"Price"	DECIMAL(10, 2) NOT NULL,
	"Image"	TEXT,
	"CreatedAt"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("ProductId" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "SavedItems" (
	"SavedItemId"	INTEGER,
	"UserId"	INTEGER,
	"ProductId"	INTEGER,
	"SavedAt"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("SavedItemId" AUTOINCREMENT),
	FOREIGN KEY("ProductId") REFERENCES "Products"("ProductId") ON DELETE CASCADE,
	FOREIGN KEY("UserId") REFERENCES "Users"("UserId") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "Users" (
	"UserId"	INTEGER,
	"Name"	VARCHAR(100),
	"Email"	VARCHAR(100) NOT NULL UNIQUE,
	"Password"	VARCHAR(255),
	"CreatedAt"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	"DisplayName"	VARCHAR(100),
	"Image"	VARCHAR(255),
	"SecurityQuestion"	TEXT,
	"SecurityAnswer"	TEXT,
	PRIMARY KEY("UserId" AUTOINCREMENT)
);
INSERT INTO "CartItems" VALUES (5,1001,1,1,'2025-06-18 21:37:08');
INSERT INTO "CartItems" VALUES (6,1001,2,2,'2025-06-18 21:48:13');
INSERT INTO "OrderDetails" VALUES (1,1,1,2,10);
INSERT INTO "OrderDetails" VALUES (2,1,2,1,7);
INSERT INTO "OrderDetails" VALUES (3,2,3,3,5);
INSERT INTO "OrderDetails" VALUES (4,2,4,1,12);
INSERT INTO "OrderDetails" VALUES (5,3,5,1,20);
INSERT INTO "OrderDetails" VALUES (6,3,6,2,50);
INSERT INTO "OrderDetails" VALUES (7,4,2,2,7);
INSERT INTO "OrderDetails" VALUES (8,4,1,1,10);
INSERT INTO "OrderDetails" VALUES (9,5,3,1,5);
INSERT INTO "OrderDetails" VALUES (10,5,5,1,20);
INSERT INTO "OrderDetails" VALUES (11,6,1,6,10);
INSERT INTO "OrderDetails" VALUES (12,7,2,1,7);
INSERT INTO "Orders" VALUES (1,1001,'2025-06-15 10:00:00',NULL,'Arriving');
INSERT INTO "Orders" VALUES (2,1001,'2025-06-15 12:30:00',NULL,'Arriving');
INSERT INTO "Orders" VALUES (3,1001,'2025-06-15 15:45:00',NULL,'Arriving');
INSERT INTO "Orders" VALUES (4,1001,'2025-06-16 09:00:00',NULL,'Arriving');
INSERT INTO "Orders" VALUES (5,1001,'2025-06-16 11:20:00',NULL,'Arriving');
INSERT INTO "Orders" VALUES (6,1001,'2025-06-19 08:58:04.067134','2025-06-24','Arriving');
INSERT INTO "Orders" VALUES (7,1001,'2025-06-19 09:01:32.366790','2025-06-24','Arriving');
INSERT INTO "Products" VALUES (1,'T-shirt','abibas',10,'products/tshirt.jfif','2025-06-11 23:05:03');
INSERT INTO "Products" VALUES (2,'Mug','milton',7,'products/mug.jfif','2025-06-11 23:05:03');
INSERT INTO "Products" VALUES (3,'Cap','yankees',5,'products/cap.jfif','2025-06-11 23:05:03');
INSERT INTO "Products" VALUES (4,'Bottle','milton',12,'products/Unknown.jpeg','2025-06-11 23:05:15');
INSERT INTO "Products" VALUES (5,'Bag','wildcraft',20,'products/bag.jpeg','2025-06-11 23:05:15');
INSERT INTO "Products" VALUES (6,'Shoes','nike',50,'products/shoes.jpeg','2025-06-11 23:05:15');
INSERT INTO "SavedItems" VALUES (3,1001,1,'2025-06-16 21:17:53');
INSERT INTO "Users" VALUES (1001,'karam','karam@gmail.com','scrypt:32768:8:1$v1eWRTMl4an7cHhE$0410bdcad723736b270c5b516b71d2a850855a0c9caa2c7f6563a5da4b578a468ae41388a49f76016aea9e12499651e009bf99b06f1bf6ef4ea1776aa47d3dd5','2025-06-16 02:21:20','karam singh','karam_account.jpeg','pet','sheru');
INSERT INTO "Users" VALUES (1002,'ItsKunal7','kunal1@gmail.com','scrypt:32768:8:1$v23nCcjhy985fmDS$949746e2e81d5c7ea022d1b0adba075b6348bd9f19b8a5e0c6e58ea904d66869f2932105c8c46768ef2851eccfe72c4d1ee48be5aabc09dbf445de1659df7248','2025-06-25 21:15:20','Kunal','ItsKunal7_images.png','pet','Sheru');
COMMIT;
