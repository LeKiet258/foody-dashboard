from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import io
from .models import *
import urllib, base64
import pandas as pd
from matplotlib.ticker import MaxNLocator
from plotly.offline import plot
import plotly.express as px

data_hcm = pd.read_csv("data/data_merge.csv")
menu = pd.read_csv("data/menu.csv")
menu_dish = pd.read_csv("data/menu_dish.csv")

# Create your views here.
def home(request):
	return HttpResponse('home')

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
	print(ret['review'])

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
