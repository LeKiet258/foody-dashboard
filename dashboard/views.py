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
	
	# review & seeding pie charts
	fig = review_seeding_ratio(vendor)
	parsed_html = BeautifulSoup(plot(fig, output_type="div"), 'html.parser')
	parsed_html.find('div')['class'] = 'center'
	parsed_html = re.sub("(<body>|</body>|<html>|</html>)", "", str(parsed_html))
	ret['review_seeding'] = parsed_html

	# menu bar-range chart
	menu_vendor = menu[menu['RestaurantID'] == res_id]
	df = menu_dish[menu_dish['RestaurantID'] == res_id].copy()
	df.drop(columns=['RestaurantID', 'dish_id', 'dish_description', 'dish_total_like', 'dish_is_available'], inplace=True)
	df = df.merge(menu_vendor.drop(columns=['RestaurantID']), on='dish_type_id', how='left').drop(columns='dish_type_id')
	fig = menu_bar(df)
	parsed_html = BeautifulSoup(plot(fig, output_type="div"), 'html.parser')
	parsed_html.find('div')['class'] = 'center'
	parsed_html = re.sub("(<body>|</body>|<html>|</html>)", "", str(parsed_html))
	ret['menu'] = parsed_html #plot(fig, output_type="div")

	### user score
	fig = user_score(vendor) # -1: ko cào dc review
	parsed_html = BeautifulSoup(plot(fig, output_type="div"), 'html.parser')
	parsed_html.find('div')['class'] = 'center'
	parsed_html = re.sub("(<body>|</body>|<html>|</html>)", "", str(parsed_html))
	ret['user_score'] = parsed_html #plot(fig, output_type="div") #

	return render(request, 'dashboard.html', ret)
    
