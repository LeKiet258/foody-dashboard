import re

def normalize_review(review):
    '''review: string'''
    if review.find("Xem thêm") != -1:
        review = review[:review.find("Xem thêm")].strip()
    if review.find("Số người") != -1: 
        review = review[:review.find("Số người")].strip()
    if review.find("Sẽ quay lại") != -1: 
        review = review[:review.find("Sẽ quay lại")].strip()
    review = re.sub(r"(“|’|”|\^\^)", '', review)

    # remove emojis
    emoji_pattern = re.compile("["
       u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U0001F1F2-\U0001F1F4"  # Macau flag
        u"\U0001F1E6-\U0001F1FF"  # flags
        u"\U0001F600-\U0001F64F"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U0001F1F2"
        u"\U0001F1F4"
        u"\U0001F620"
        u"\u200d"
        u"\u2640-\u2642"
        "]+", 
        flags=re.UNICODE)
    review = emoji_pattern.sub(r'', review)                           

    # remove redundant punctuation
    review = re.sub(r'(\W)(?=\1)', '', review)

    # xoá khoảng trống trước dấu fẩy & chấm
    review = re.sub(r'\s+,', r',', review)
    review = re.sub(r'\s+[.]', r'.', review)

    new_text = []
    for sen in review.split("."):
        if sen.replace(" ", ""):
            new_text.append(sen.strip())
    review = '. '.join(new_text)

    return review

def reduce_price(price):
    if price < 1e6:
        price = str(price/1e3)
        if int(price.split(".")[-1]) == 0: 
            price = price.split(".")[0]
        return price + 'K'
    else:
        price = str(price/1e6)
        if int(price.split(".")[-1]) == 0: 
            price = price.split(".")[0]
        return price + 'M'