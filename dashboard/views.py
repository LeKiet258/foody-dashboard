from django.shortcuts import render
from django.http import HttpResponse
from .models import *
import urllib, base64
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

data_hcm = pd.read_csv("data/data_merge.csv")
menu = pd.read_csv("data/menu.csv")
menu_dish = pd.read_csv("data/menu_dish.csv")

# Create your views here.
def home(request):
	# global data_hcm
	res = Vendor.objects.all() # bắt buộc dùng db
	paginator = Paginator(res, 25) # Show 25 res per page.
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)

	return render(request, 'foody_dashboard/smallfood.html', {'page_obj': page_obj})


def dashboard(request, res_id):
	global data_hcm, menu, menu_dish
	ret = {}
	# res_id = 90018
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
	ret['menu'] = plot(fig, output_type="div") #plot(fig, output_type="div")

	### user score
	fig = user_score(vendor) # -1: ko cào dc review
	parsed_html = BeautifulSoup(plot(fig, output_type="div"), 'html.parser')
	parsed_html.find('div')['class'] = 'center'
	parsed_html = re.sub("(<body>|</body>|<html>|</html>)", "", str(parsed_html))
	ret['user_score'] = plot(fig, output_type="div") #parsed_html # #

	# component score
	fig = component_score(vendor)
	ret['component_score'] = plot(fig, output_type="div")

	return render(request, 'dashboard.html', ret)
    
