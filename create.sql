CREATE TABLE Reviews(review_id INTEGER NOT NULL PRIMARY KEY,
                     product_id INTEGER NOT NULL REFERENCES Items(product_id),
                     seller_username VARCHAR(30) NOT NULL REFERENCES Buyers(username),
                     buyer_username VARCHAR(30) NOT NULL REFERENCES Buyers(username),
                     item_rating INTEGER NOT NULL CHECK(item_rating > 0 AND item_rating <= 5),
                     comments VARCHAR(2000));

CREATE TABLE Buyers(username VARCHAR(30) NOT NULL PRIMARY KEY,
                    is_seller BOOLEAN NOT NULL,
                    bio VARCHAR(200),
                    name VARCHAR(30) NOT NULL,
                    password VARCHAR(30) NOT NULL,
                    address VARCHAR(200));

CREATE TABLE Orders(order_id INTEGER NOT NULL PRIMARY KEY,
                    buyer_username VARCHAR(30) NOT NULL REFERENCES Buyers(username),
                    tracking_num INTEGER NOT NULL,
                    date_returned DATE,
                    date_ordered DATE NOT NULL,
                    shipping_status VARCHAR(30) NOT NULL));


CREATE TABLE Items(product_id INTEGER NOT NULL PRIMARY KEY,
                  seller_username VARCHAR(30) NOT NULL REFERENCES Buyers(username),
                  category VARCHAR(80),
                  condition VARCHAR(30),
                  item_name VARCHAR(80) NOT NULL,
                  price DECIMAL(10,2) CHECK(price > 0),
                  quantity INTEGER NOT NULL CHECK(quantity > 0),
                  image VARCHAR(500),
                  description VARCHAR(2000));


CREATE TABLE inOrder(product_id INTEGER NOT NULL REFERENCES Items(product_id),
                    seller_username VARCHAR(30) NOT NULL REFERENCES Buyers(username),
                    order_id INTEGER NOT NULL REFERENCES Orders(order_id),
                    order_quantity INTEGER NOT NULL CHECK(order_quantity > 0),
                    PRIMARY KEY(product_id, seller_username, order_id));

CREATE TABLE inWishlist(product_id INTEGER NOT NULL REFERENCES Items(product_id),
                    seller_username VARCHAR(30) NOT NULL REFERENCES Buyers(username),
                    buyer_username VARCHAR(30) NOT NULL REFERENCES Buyers(username) CHECK(buyer_username <> seller_username),
                    wishlist_quantity INTEGER NOT NULL CHECK(wishlist_quantity > 0),
                    PRIMARY KEY(product_id, seller_username, buyer_username));

CREATE TABLE inCart(product_id INTEGER NOT NULL REFERENCES Items(product_id),
                    seller_username VARCHAR(30) NOT NULL REFERENCES Buyers(username),
                    buyer_username VARCHAR(30) NOT NULL REFERENCES Buyers(username) CHECK(buyer_username <> seller_username),
                    cart_quantity INTEGER NOT NULL CHECK(cart_quantity > 0),
                    PRIMARY KEY(product_id, seller_username, buyer_username));
