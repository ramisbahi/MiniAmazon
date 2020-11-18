import random

# Code to generate reviews for products. This code should be copied
# into app.py and called from there in order for it to be run properly

reviews = [
    (1, 'This is honestly one of the worst products I have ever used.', 'deansawaf'),
    (1, 'Terrible! Do not buy this', 'Macaward'),
    (2, 'Pretty mediocre TBH, the only saving grace was the fact that it was pretty cheap', 'OldAnt'),
    (3, 'Definitely got some great use out of this product. Not the highest end, but still served its purpose.', 'VenomSpider'),
    (3, 'Thank you to whoever made this product! The price was a bit high for sure, but that is my only complaint', 'HammerGoat'),
    (3, 'My product had a defect, but luckily customer service was quick to respond which made up for it', 'SimpleBoomer'),
    (4, 'Love it! I use it all the time.', 'HollowCalf'),
    (4, 'I enjoyed using this product', 'IcySpecter'),
    (5, 'LOVE IT SO MUCH!!!!!', 'Gamermaid'),
    (5, 'If I could I would give this 10 stars, use it every single day. Top notch', 'Chimpanther'),
    (5, 'Great product, would highly recommend this to anyone considering the purchase.', 'Beezenees'),
]


def generate_reviews(product_id, seller_username):
    all_reviews = []

    for i in range(random.randint(0, 2)):
        try:
            new_review = models.Reviews()
            new_review.product_id = product_id
            new_review.seller_username = seller_username

            rand_review = reviews[random.randint(0, len(reviews) - 1)]

            new_review.item_rating = rand_review[0]
            new_review.comments = rand_review[1]
            new_review.buyer_username = rand_review[2]

            all_reviews.append(new_review)

        except Exception:
            print('AN ERROR OCCURRED!!!!!')

    db.session.add_all(all_reviews)
    db.session.commit()
