from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import io
from .models import *
import urllib, base64
import pandas as pd

data_hcm = pd.read_csv("dashboard/data_merge.csv")

# Create your views here.
def home(request):
    global data_hcm
    ret = {}

    ### Review ###
    vendor = data_hcm.loc[data_hcm['RestaurantId'] == 5469.0, ["nExcellentReviews", "nGoodReviews", "nAverageReviews", "nBadReviews"]]
    vendor = vendor.T[0]
    fig = plt.figure(figsize=(7,7))
    ax = plt.subplot(111)

    labels = [str("{:.2f}%".format(100*vendor[0]/ vendor.sum())), 
            str("{:.2f}%".format(100*vendor[1]/ vendor.sum())), 
            str("{:.2f}%".format(100*vendor[2]/ vendor.sum())),
            '']
    ax.pie(vendor, startangle = 90, labels=labels)
    lgd = ax.legend([i for i in vendor.index], bbox_to_anchor=(0.1, 1.05))

    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_extra_artists=(lgd,), bbox_inches='tight')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    ret['data'] = uri

    ### Score ###

    return render(request, 'review.html', ret)

    # return HttpResponse('home')