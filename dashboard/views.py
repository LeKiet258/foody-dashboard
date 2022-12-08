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

cuisines_list = ['Bánh Pizza', 'Hà Nội', 'Miền Đông', 'Campuchia', 'Tây Ban Nha', 'Mỹ', 'Pháp', 'Nam Định', 'Đài Loan', 'Tây Bắc', 'Á', 'Úc', 'Âu', 'Đặc biệt', 'Đặc sản vùng', 'Đức', 'Buôn Mê', 'Iran', 'Châu Phi', 'Bắc Âu', 'Ý', 'Mexico', 'Đà Lạt', 'Philippines', 'Bình Định', 'Ấn Độ', 'Canada', 'Miền Nam', 'Tiệp (Séc)', 'Malaysia', 'Trung Đông', 'Quốc tế', 'Hàn', 'Nha Trang', 'Thổ Nhĩ Kỳ', 'Đông Âu', 'Brazil', 'Việt', 'Quảng', 'Thái', 'Ả Rập', 'Nhật', 'Miền Tây', 'Tây Nguyên', 'Bắc', 'Trung Hoa', 'Huế', 'Singapore', 'Miền Trung', 'Châu Mỹ']
districts_list = ['Quận 1', 'Quận 3', 'Quận Phú Nhuận', 'Quận 5', 'Quận Tân Bình', 'Quận Bình Thạnh', 'Quận 11', 'Quận 10','Quận Tân Phú', 'Quận Bình Tân', 'Quận 8', 'Quận Gò Vấp', 'Quận 4', 'Tp. Thủ Đức', 'Quận 7', 'Quận 9', 'Quận 6', 'Quận 2','Huyện Nhà Bè', 'Quận 12', 'Huyện Hóc Môn', 'Huyện Bình Chánh', 'Huyện Củ Chi'] 
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

            return render(request, 'foody_dashboard/smallfood.html', {'page_obj': page_obj, 'cuisines': cuisines_list, 'districts': districts_list})

    return render(request, 'foody_dashboard/smallfood.html', {'page_obj': page_obj, 'cuisines': cuisines_list, 'districts': districts_list})


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
	parsed_html.find('div')['class'] = 'grid-child purple'
	parsed_html = re.sub("(<body>|</body>|<html>|</html>)", "", str(parsed_html))
	ret['review_seeding'] = plot(fig, output_type="div")

	# component score
	fig = component_score(vendor)
	parsed_html = BeautifulSoup(plot(fig, output_type="div"), 'html.parser')
	parsed_html.find('div')['class'] = 'grid-child green'
	parsed_html = re.sub("(<body>|</body>|<html>|</html>)", "", str(parsed_html))
	ret['component_score'] = parsed_html

	# menu bar-range chart
	menu_vendor = menu[menu['RestaurantID'] == res_id]
	df = menu_dish[menu_dish['RestaurantID'] == res_id].copy()
	df.drop(columns=['RestaurantID', 'dish_id', 'dish_description', 'dish_total_like', 'dish_is_available'], inplace=True)
	df = df.merge(menu_vendor.drop(columns=['RestaurantID']), on='dish_type_id', how='left').drop(columns='dish_type_id')
	fig = menu_bar(df)
	parsed_html = BeautifulSoup(plot(fig, output_type="div"), 'html.parser')
	parsed_html.find('div')['class'] = 'relative'
	parsed_html = re.sub("(<body>|</body>|<html>|</html>)", "", str(parsed_html))
	ret['menu'] = parsed_html

	### user score
	fig = user_score_bar(vendor) # -1: ko cào dc review
	parsed_html = BeautifulSoup(plot(fig, output_type="div"), 'html.parser')
	parsed_html.find('div')['class'] = 'center2'
	parsed_html = re.sub("(<body>|</body>|<html>|</html>)", "", str(parsed_html))
	ret['user_score'] = parsed_html

	

	

	return render(request, 'dashboard.html', ret)
