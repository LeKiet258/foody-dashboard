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

data_hcm = pd.read_csv("dashboard/data/data_merge.csv")
menu = pd.read_csv("dashboard/data/menu.csv")
menu_dish = pd.read_csv("dashboard/data/menu_dish.csv")

# Create your views here.
def home(request):
	#global data_hcm
	res = Vendor.objects.all()
	for r in range(len(res)):
		cui = ''
		temp = res[r].cuisines[1:len(res[r].cuisines)-1].split(", ")
		for t in temp:
			t = t[1:len(t)-1].split('Món ')[-1]
			cui += t + ', '
		res[r].cuisines = cui[:-2]

		res[r].AvgScore = round(res[r].AvgScore,1)

		res[r].min_price = int(res[r].min_price)
		res[r].max_price = int(res[r].max_price)
		if res[r].max_price != -1:
			if res[r].min_price <= 999999:
				nghin = int(res[r].min_price/1000)
				res[r].min_price = str(nghin) + 'K'
			else: #1 250 000
				if res[r].min_price % 1000000 == 0:
					trieu = int(res[r].min_price/1000000)
				else:
					trieu = (res[r].min_price/1000000)
				res[r].min_price = str(trieu) + 'M'

			if res[r].max_price <= 999999:
				nghin = int(res[r].max_price/1000)
				res[r].max_price = str(nghin) + 'K'
			else: #1 250 000
				if res[r].max_price % 1000000 == 0:
					trieu = int(res[r].max_price/1000000)
				else:
					trieu = res[r].max_price/1000000

				res[r].max_price = str(trieu) + 'M'


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
		

	paginator = Paginator(res, 25) # Show 25 res per page.

	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)

	#review = Vendor.objects.get()

	return render(request, 'foody_dashboard/smallfood.html', {'page_obj': page_obj})


def dashboard(request):
	global data_hcm, menu, menu_dish
	ret = {}
	res_id = 90018
	vendor = data_hcm.loc[data_hcm['RestaurantId'] == res_id]
	
	### Review ###
	df = vendor[["nExcellentReviews", "nGoodReviews", "nAverageReviews", "nBadReviews"]]
	df = df.T[[1]]
	df.rename(index={'nExcellentReviews': 'Tuyệt vời', 
					'nGoodReviews': 'Tốt',
					'nAverageReviews': 'Trung bình',
					'nBadReviews': 'Tệ'}, inplace=True)
	df = df.reset_index().rename(columns={"index": "loại review", 1: "số người"})

	fig = px.pie(df, values='số người', names='loại review', title='Tỷ lệ từng loại review của quán', width=500, height=400)
	fig.update_layout(title_x=0.5)
	ret['review'] = plot(fig, output_type="div")

	### Seeding ###
	vendor = data_hcm.loc[data_hcm['RestaurantId'] == res_id]

	df = vendor[["seeding_pct"]]
	df = df.T[[1]]
	df = df.rename(index={'seeding_pct': 'seeding'}, columns={1: "Tỷ lệ"}).reset_index().rename(columns={'index': 'Loại'})
	df.loc[1] = ["trung thực", 1 - df.iloc[0, 1]]

	fig = px.pie(df, values='Tỷ lệ', names='Loại', title='Tỷ lệ seeding của quán', width=500, height=400)
	fig.update_layout(title_x=0.5)
	ret['seeding'] = plot(fig, output_type="div")

	### Score ###
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