CREATE TABLE Reviews(review_id SERIAL PRIMARY KEY,
                     product_id VARCHAR(30) NOT NULL,
                     seller_username VARCHAR(30) NOT NULL,
                     buyer_username VARCHAR(30) NOT NULL REFERENCES Buyers(username),
                     item_rating INTEGER NOT NULL CHECK(item_rating > 0 AND item_rating <= 5),
                     comments VARCHAR(2000),
                     FOREIGN KEY(product_id, seller_username) REFERENCES Items(product_id, seller_username));

CREATE TABLE Buyers(username VARCHAR(30) NOT NULL PRIMARY KEY,
                    is_seller BIT NOT NULL,
                    bio VARCHAR(200),
                    name VARCHAR(30) NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    address VARCHAR(800),
                    maiden VARCHAR(30) NOT NULL); /*changed to 800*/

INSERT INTO Buyers VALUES('ramisbahi', TRUE, 'I am cool', 'Rami Sbahi', 'superman', '3200 Jam Court\nDurham, NC 27708\nUnited States');
INSERT INTO Buyers VALUES('chrisyang', TRUE, 'I am not very cool', 'Chris Yang', 'spiderman', '3000 Yang Court\nDurham, NC 27708\nUnited States');
INSERT INTO Buyers VALUES('joshguo', FALSE, 'I am the man the myth the legend', 'Josh Guo', 'IRONMAN', '1200 Yeet Drive\nDurham, NC 27708\nUnited States');
INSERT INTO Buyers VALUES('DonaldTrump', FALSE, 'I am the president', 'DJT', 'Swampman', 'White House');


CREATE TABLE Orders(order_id SERIAL NOT NULL PRIMARY KEY,
                    buyer_username VARCHAR(30) NOT NULL REFERENCES Buyers(username),
                    tracking_num SERIAL NOT NULL,
                    date_returned DATE,
                    date_ordered DATE NOT NULL);


CREATE TABLE Items(product_id VARCHAR(30) NOT NULL, /*just changed to string*/
                  seller_username VARCHAR(30) NOT NULL REFERENCES Buyers(username),
                  category VARCHAR(100), /*Sports, */
                  condition VARCHAR(30), /*New, Used - Like New, Used - Very Good, Used - Good, Used - Acceptable*/
                  item_name VARCHAR(500) NOT NULL,
                  price DECIMAL(10,2) CHECK(price > 0),
                  quantity INTEGER NOT NULL CHECK(quantity > 0),
                  image VARCHAR(1000),
                  description VARCHAR(2000),
                  PRIMARY KEY(product_id, seller_username));

INSERT INTO Items VALUES(1, 'ramisbahi', 'Sports', 'New', 'Spalding Basketball', 25.50, 10, 'https://www.spalding.com/dw/image/v2/ABAH_PRD/on/demandware.static/-/Sites-masterCatalog_SPALDING/default/dwd21974bc/images/hi-res/74876E_FRONT.jpg?sw=555&sh=689&sm=cut&sfrm=jpg', 'Bounces like no other.');


CREATE TABLE inorder(product_id VARCHAR(30) NOT NULL,
                    seller_username VARCHAR(30) NOT NULL,
                    order_id INTEGER NOT NULL REFERENCES Orders(order_id),
                    order_quantity INTEGER NOT NULL CHECK(order_quantity > 0),
                    PRIMARY KEY(product_id, seller_username, order_id),
                    FOREIGN KEY(product_id, seller_username) REFERENCES Items(product_id, seller_username));

CREATE TABLE inwishlist(product_id VARCHAR(30) NOT NULL,
                    seller_username VARCHAR(30) NOT NULL,
                    buyer_username VARCHAR(30) NOT NULL REFERENCES Buyers(username) CHECK(buyer_username <> seller_username),
                    wishlist_quantity INTEGER NOT NULL CHECK(wishlist_quantity > 0),
                    PRIMARY KEY(product_id, seller_username, buyer_username),
                    FOREIGN KEY(product_id, seller_username) REFERENCES Items(product_id, seller_username));

INSERT INTO inwishlist VALUES(1, 'ramisbahi', 'joshguo', 1);

CREATE TABLE incart(product_id VARCHAR(30) NOT NULL,
                    seller_username VARCHAR(30) NOT NULL,
                    buyer_username VARCHAR(30) NOT NULL REFERENCES Buyers(username) CHECK(buyer_username <> seller_username),
                    cart_quantity INTEGER NOT NULL CHECK(cart_quantity > 0),
                    PRIMARY KEY(product_id, seller_username, buyer_username),
                    FOREIGN KEY(product_id, seller_username) REFERENCES Items(product_id, seller_username));
