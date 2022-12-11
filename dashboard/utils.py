import re
import pandas as pd
import numpy as np
import textwrap

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

def process_review_px(
    review,
    intervals = [[1, 2], [2,3], [3, 4], [4,5], [5, 6], [6,7], [7, 8], [8,9], [9, 10]]):

    # review = vendor['Reviews'].iloc[0]
    review = eval(review)
    review_dict ={'Usernames': [], 'Date': [], 'Title': [], 'Body': [], 'is_returned': [], 'User_score': []}
    for single_rv in review:
        for k in review_dict.keys():
            review_dict[k].append(single_rv[k])

    review_df = pd.DataFrame.from_dict(review_dict)
    review_df = review_df[review_df['User_score'] != 0] # loại các review có đánh giá 0.0 vì đa fần là qc
    review_df['Body'] = review_df['Body'].apply(normalize_review)
    review_df['group'] = np.nan
    for i in range(review_df.shape[0]):
        for interval in intervals:
            if interval[0] <= float(review_df.iloc[i, -2]) < interval[1]:
                review_df.iloc[i, -1] = str(interval)
                break
    review_df = review_df.groupby('group').head(3)     
    hoverinfo_ls = [np.nan] * len(intervals)
    for i, interval in enumerate(intervals):
        tmp = review_df.loc[review_df['group'] == str(interval), 'Body']
        if not tmp.empty:
            tmp = tmp.to_list()
            for j in range(len(tmp)):
                if len(tmp[j]) > 1500:
                    tmp[j] = tmp[j][:1500] + "..(còn nữa)"
                tmp[j] = '<br>'.join(textwrap.wrap(tmp[j], 150))
            hoverinfo_ls[i] = '<br><br>'.join(tmp) + "<extra></extra>"
    return hoverinfo_ls

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