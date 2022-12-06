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
import pdb
import ast

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
	#print(res_id)
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
	
	fig = review_seeding_ratio(vendor)
	ret['review_seeding'] = plot(fig, output_type="div")




	## Score ###
	review = vendor['Reviews'].to_list()
	review = eval(review[0])
	user_score = [user['User_score'] for user in review]
	user_score = list(filter(lambda a: a != 0, user_score)) # filter user cho 0d (thường là các advert)	

	fig, ax = plt.subplots(1,1, figsize=(15,7))
	df = pd.Series(user_score).value_counts()
	df.index = df.index.astype(float)
	df.sort_index(ascending=True).plot.bar(ax=ax, rot=0)

	xticklabels = ax.get_xticklabels()
	for i, tick in enumerate(xticklabels):
		if float(tick.get_text()) < 6.0:
			ax.get_children()[i].set_color('brown')

	# ax.xaxis.set_major_locator(MaxNLocator(integer=True))
	ax.grid(axis='y')
	ax.set(xlabel="Điểm (thang 10)", ylabel="Số người", title=f"Điểm số đánh giá của {len(user_score)} người dùng")

	#convert graph into dtring buffer and then we convert 64 bit code into image
	buf = io.BytesIO()
	fig.savefig(buf, format='png')
	buf.seek(0)
	string = base64.b64encode(buf.read())
	uri = urllib.parse.quote(string)
	ret['score'] = uri

	### Menu ###
	menu_vendor = menu[menu['RestaurantID'] == res_id]
	df = menu_dish[menu_dish['RestaurantID'] == res_id].copy()
	df.drop(columns=['RestaurantID', 'dish_id', 'dish_description', 'dish_total_like', 'dish_is_available'], inplace=True)
	df = df.merge(menu_vendor.drop(columns=['RestaurantID']), on='dish_type_id', how='left').drop(columns='dish_type_id')
	df = df.groupby('dish_type_name').agg({'dish_price_value': ['min', 'max']})['dish_price_value']
	
	fig, ax = plt.subplots(1,1, figsize=(7,7))
	ax.barh(range(len(df['max'])), width=[h-b for h, b in zip(df['max'], df['min'])], left=df['min'], align='center')
	ax.set_yticks(range(len(df.index.to_list())), df.index.to_list(), size='small', rotation=0)
	ax.set_xticks(ax.get_xticks())
	ax.grid(axis='x')
	ax.set_title("Thực đơn")
	#convert graph into dtring buffer and then we convert 64 bit code into image
	buf = io.BytesIO()
	fig.savefig(buf, format='png', bbox_inches="tight")
	buf.seek(0)
	string = base64.b64encode(buf.read())
	uri = urllib.parse.quote(string)
	ret['menu'] = uri

	return render(request, 'dashboard.html', ret)
    
