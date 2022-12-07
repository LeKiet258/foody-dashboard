from django.shortcuts import render
from django.http import HttpResponse
from .models import *
import urllib
import base64
import pandas as pd
from matplotlib.ticker import MaxNLocator
from plotly.offline import plot
import plotly.express as px
from django.core.paginator import Paginator
import io
import matplotlib.pyplot as plt
from .viz import *
from bs4 import BeautifulSoup
import pdb
import ast
import re

from underthesea import word_tokenize

data_hcm = pd.read_csv("data/data_merge.csv")
menu = pd.read_csv("data/menu.csv")
menu_dish = pd.read_csv("data/menu_dish.csv")

# Create your views here.
def home(request):
    # global data_hcm
    res = Vendor.objects.all()
    for r in range(len(res)):
        cui = ''
        temp = res[r].cuisines[1:len(res[r].cuisines)-1].split(", ")
        for t in temp:
            t = t[1:len(t)-1].split('Món ')[-1]
            cui += t + ', '
        res[r].cuisines = cui[:-2]

        res[r].AvgScore = round(res[r].AvgScore, 1)

        res[r].min_price = int(res[r].min_price)
        res[r].max_price = int(res[r].max_price)
        res[r].TotalViews = int(res[r].TotalViews)
        if res[r].seeding_pct == '':
            res[r].seeding_pct = 0
        elif res[r].seeding_pct == '1.00':
            res[r].seeding_pct = 100
        else:
            if len(res[r].seeding_pct.split('.')[1]) == 1:
                res[r].seeding_pct = int(res[r].seeding_pct.split('.')[1])*10
            else:
                res[r].seeding_pct = int(res[r].seeding_pct.split('.')[1])

    paginator = Paginator(res, 25)  # Show 25 res per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # review = Vendor.objects.get()

    # search Khải add
    if request.method == 'POST':
        search = request.POST.get('search')
        searchPares = word_tokenize(search)

        finalVendors = []
        for searchPare in searchPares:
            for vendor in res:
                if searchPare.lower() in vendor.Name.lower() and vendor not in finalVendors:
                    finalVendors.append(vendor)

        context = {'vendors': finalVendors}

        if len(finalVendors) == 0:
            return render(request, 'search/emptyPage.html', context)

        else:
            # tạm thời chưa cho phân trang.
            paginator = Paginator(finalVendors, len(finalVendors))
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            return render(request, 'foody_dashboard/smallfood.html', {'page_obj': page_obj})

    return render(request, 'foody_dashboard/smallfood.html', {'page_obj': page_obj})


def dashboard(request, res_id):
	global data_hcm, menu, menu_dish
	ret = {}
	vendor = data_hcm.loc[data_hcm['RestaurantId'] == res_id]

	coupons = []

	for i in range(len(ast.literal_eval(vendor['expired'].item()))):
		coupons.append({'expired': ast.literal_eval(vendor['expired'].item())[i], 
		'promo_description': ast.literal_eval(vendor['promo_description'].item())[i], 
		'promo_code': ast.literal_eval(vendor['promo_code'].item())[i], 
		'discount': "{:,}".format(int(ast.literal_eval(vendor['max_discount_value'].item())[i]))})

	ret['page'] = vendor['ReviewUrl'].item()
	ret['name'] = vendor['Name'].item()
	ret['address'] = vendor['Address'].item()
	ret['isdelivery'] = vendor['IsDelivery'].item()
	ret['mincharge'] = '{:,}'.format(int(vendor['min_charge'].item()))
	ret['extrainfo'] = vendor['ExtraInfo'].item()
	ret['opentime'] = vendor['OpenTime'].item()
	ret['totalpics'] = vendor['TotalPictures'].item()
	ret['totalviews'] = vendor['TotalViews'].item()
	ret['totalsaves'] = vendor['TotalSaves'].item()
	ret['capacity'] = vendor['Capacity'].item()
	ret['servicefee'] = "{:,}".format(int(vendor['service_fee'].item()))
	ret['minshipfee'] = "{:,}".format(int(vendor['minimun_shiping_fee'].item()))
	ret['coupons'] = coupons
	
	# review & seeding pie charts
	fig = review_seeding_ratio(vendor)
	parsed_html = BeautifulSoup(plot(fig, output_type="div"), 'html.parser')
	parsed_html.find('div')['class'] = 'center'
	parsed_html = re.sub("(<body>|</body>|<html>|</html>)", "", str(parsed_html))
	ret['review_seeding'] = plot(fig, output_type="div")

	# menu bar-range chart
	menu_vendor = menu[menu['RestaurantID'] == res_id]
	df = menu_dish[menu_dish['RestaurantID'] == res_id].copy()
	df.drop(columns=['RestaurantID', 'dish_id', 'dish_description', 'dish_total_like', 'dish_is_available'], inplace=True)
	df = df.merge(menu_vendor.drop(columns=['RestaurantID']), on='dish_type_id', how='left').drop(columns='dish_type_id')
	fig = menu_bar(df)
	parsed_html = BeautifulSoup(plot(fig, output_type="div"), 'html.parser')
	parsed_html.find('div')['class'] = 'center'
	parsed_html = re.sub("(<body>|</body>|<html>|</html>)", "", str(parsed_html))
	ret['menu'] = plot(fig, output_type="div") 

	### user score
	fig = user_score_bar(vendor) # -1: ko cào dc review
	parsed_html = BeautifulSoup(plot(fig, output_type="div"), 'html.parser')
	parsed_html.find('div')['class'] = 'center2'
	parsed_html = re.sub("(<body>|</body>|<html>|</html>)", "", str(parsed_html))
	ret['user_score'] = parsed_html
	##
	screen_width = 1366
	fig_width = 800	  
	ret['start_px'] = 2139.213 / 2 # px/2

	# component score
	fig = component_score(vendor)
	ret['component_score'] = plot(fig, output_type="div")

	

	return render(request, 'dashboard.html', ret)
