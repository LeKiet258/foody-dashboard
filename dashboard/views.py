from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import io
from .models import *
import urllib, base64
import pandas as pd
from matplotlib.ticker import MaxNLocator

data_hcm = pd.read_csv("data/data_merge.csv")

# Create your views here.
def home(request):
    global data_hcm
    ret = {}
    vendor = data_hcm.loc[data_hcm['RestaurantId'] == 5469.0]

    ### Review ###
    df = vendor[["nExcellentReviews", "nGoodReviews", "nAverageReviews", "nBadReviews"]]
    df = df.T[0]
    fig = plt.figure(figsize=(7,7))
    ax = plt.subplot(111)

    labels = [str("{:.2f}%".format(100*df[0]/ df.sum())), 
            str("{:.2f}%".format(100*df[1]/ df.sum())), 
            str("{:.2f}%".format(100*df[2]/ df.sum())),
            '']
    ax.pie(df, startangle = 90, labels=labels)
    lgd = ax.legend([i for i in df.index], bbox_to_anchor=(0.1, 1.05))

    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_extra_artists=(lgd,), bbox_inches='tight')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    ret['data'] = uri

    ### Score ###
    review = vendor['Reviews'][0]
    review = eval(review)
    user_score = [user['User_score'] for user in review]
    user_score = list(filter(lambda a: a != 0, user_score)) # filter user cho 0d (thường là các advert)

    fig, ax = plt.subplots(1,1, figsize=(7,7))
    pd.Series(user_score).value_counts().plot.barh(ax=ax)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis='x')
    ax.set(xlabel="Số người đánh giá", ylabel="Điểm (thang 10)", title=f"Điểm số đánh giá của {len(user_score)} người dùng")

    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    ret['review'] = uri

    return render(request, 'review.html', ret)

    # return HttpResponse('home')