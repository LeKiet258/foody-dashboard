from django.shortcuts import render
from django.http import HttpResponse
from .models import *
import pandas as pd
from plotly.offline import plot
from django.core.paginator import Paginator
from .viz import *
from bs4 import BeautifulSoup
import pdb
import ast
import dateutil.parser as dparser
import re
from underthesea import word_tokenize

data_hcm = pd.read_csv("data/data_merge.csv")
menu = pd.read_csv("data/menu.csv")
menu_dish = pd.read_csv("data/menu_dish.csv")

cuisines_list = ['Bánh Pizza', 'Hà Nội', 'Miền Đông', 'Campuchia', 'Tây Ban Nha', 'Mỹ', 'Pháp', 'Nam Định', 'Đài Loan', 'Tây Bắc', 'Á', 'Úc', 'Âu', 'Đặc biệt', 'Đặc sản vùng', 'Đức', 'Buôn Mê', 'Iran', 'Châu Phi', 'Bắc Âu', 'Ý', 'Mexico', 'Đà Lạt', 'Philippines', 'Bình Định',
                 'Ấn Độ', 'Canada', 'Miền Nam', 'Tiệp (Séc)', 'Malaysia', 'Trung Đông', 'Quốc tế', 'Hàn', 'Nha Trang', 'Thổ Nhĩ Kỳ', 'Đông Âu', 'Brazil', 'Việt', 'Quảng', 'Thái', 'Ả Rập', 'Nhật', 'Miền Tây', 'Tây Nguyên', 'Bắc', 'Trung Hoa', 'Huế', 'Singapore', 'Miền Trung', 'Châu Mỹ']
districts_list = ['Quận 1', 'Quận 3', 'Quận Phú Nhuận', 'Quận 5', 'Quận Tân Bình', 'Quận Bình Thạnh', 'Quận 11', 'Quận 10', 'Quận Tân Phú', 'Quận Bình Tân', 'Quận 8',
                  'Quận Gò Vấp', 'Quận 4', 'Tp. Thủ Đức', 'Quận 7', 'Quận 9', 'Quận 6', 'Quận 2', 'Huyện Nhà Bè', 'Quận 12', 'Huyện Hóc Môn', 'Huyện Bình Chánh', 'Huyện Củ Chi']
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
        res[r].AvgScore = round(
            res[r].AvgScore, 1) if res[r].AvgScore > 0 else ''

        res[r].TotalReviews = res[r].nBadReviews + res[r].nAverageReviews + \
            res[r].nGoodReviews + res[r].nExcellentReviews
        if res[r].TotalReviews < 0:
            res[r].TotalReviews = ''

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

            return render(request, 'smallfood.html', {'page_obj': page_obj, 'cuisines': cuisines_list, 'districts': districts_list})

    return render(request, 'smallfood.html', {'page_obj': page_obj, 'cuisines': cuisines_list, 'districts': districts_list})


def compare_2_vendors(request, res_id1 = 90018, res_id2 = 44868):
    if request.method == 'GET':
        try:
            shops = request.GET.getlist('shop-selected')
            [res_id1, res_id2] = [eval(i) for i in shops]
        except:
            [res_id1, res_id2] = [90018, 44868]

    global data_hcm, menu, menu_dish
    vendor = data_hcm.loc[(data_hcm['RestaurantId'] == res_id1) | (
        data_hcm['RestaurantId'] == res_id2)]
    ret = {}
    compare_items = []

    for i in [res_id1, res_id2]:
        coupons = []
        for j in range(len(ast.literal_eval(vendor.loc[vendor.RestaurantId == i, 'expired'].item()))):
            coupons.append({'expired': ast.literal_eval(vendor.loc[vendor.RestaurantId == i, 'expired'].item())[j],
            'promo_description': ast.literal_eval(vendor.loc[vendor.RestaurantId == i, 'promo_description'].item())[j],
            'promo_code': ast.literal_eval(vendor.loc[vendor.RestaurantId == i, 'promo_code'].item())[j],
            'discount': "{:,}".format(int(ast.literal_eval(vendor.loc[vendor.RestaurantId == i, 'max_discount_value'].item())[j]))})

        compare_items.append({'id': i,
        'name': vendor.loc[vendor.RestaurantId == i, 'Name'].item(),
        'totalviews': vendor.loc[vendor.RestaurantId == i, 'TotalViews'].item(),
        'totalreviews': vendor.loc[vendor.RestaurantId == i, 'TotalReviews'].item(),
		'isdelivery': vendor.loc[vendor.RestaurantId == i, 'IsDelivery'].item(),
		'minshipfee': vendor.loc[vendor.RestaurantId == i, 'minimun_shiping_fee'].item(),
		'capacity': vendor.loc[vendor.RestaurantId == i, 'Capacity'].item(),
		'mincharge': "{:,}".format(int(vendor.loc[vendor.RestaurantId == i, 'min_charge'].item())),
		'servicefee': "{:,}".format(int(vendor.loc[vendor.RestaurantId == i, 'service_fee'].item())),
		'minprice': "{:,}".format(int(vendor.loc[vendor.RestaurantId == i, 'min_price'].item())),
		'maxprice': "{:,}".format(int(vendor.loc[vendor.RestaurantId == i, 'max_price'].item())),
        'coupons': coupons})

    ret['items'] = compare_items

    # review type
    fig = compare_review_type(vendor)
    ret['review_type'] = plot(fig, output_type="div")

    # seeding
    fig = compare_seeding(vendor)
    ret['seeding'] = plot(fig, output_type="div")

    # user_score
    fig = compare_user_score(vendor)
    ret['user_score'] = plot(fig, output_type="div")

    # component score
    fig = compare_component_score(vendor)
    ret['component_score'] = plot(fig, output_type="div")

    return render(request, 'compare.html', ret)


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
    ret['minshipfee'] = "{:,}".format(
        int(vendor['minimun_shiping_fee'].item()))
    ret['img'] = vendor['PagePic'].item()
    ret['coupons'] = coupons

    # review & seeding pie charts
    fig = review_seeding_ratio(vendor)
    parsed_html = BeautifulSoup(plot(fig, output_type="div"), 'html.parser')
    parsed_html.find('div')['class'] = 'grid-child purple'
    parsed_html = re.sub("(<body>|</body>|<html>|</html>)",
                         "", str(parsed_html))
    ret['review_seeding'] = plot(fig, output_type="div")

    # component score
    fig = component_score(vendor)
    parsed_html = BeautifulSoup(plot(fig, output_type="div"), 'html.parser')
    parsed_html.find('div')['class'] = 'grid-child green'
    parsed_html = re.sub("(<body>|</body>|<html>|</html>)",
                         "", str(parsed_html))
    ret['component_score'] = parsed_html

    # menu bar-range chart
    menu_vendor = menu[menu['RestaurantID'] == res_id]
    df = menu_dish[menu_dish['RestaurantID'] == res_id].copy()
    df.drop(columns=['RestaurantID', 'dish_id', 'dish_description',
            'dish_total_like', 'dish_is_available'], inplace=True)
    df = df.merge(menu_vendor.drop(columns=[
                  'RestaurantID']), on='dish_type_id', how='left').drop(columns='dish_type_id')
    fig = menu_bar(df)
    parsed_html = BeautifulSoup(plot(fig, output_type="div"), 'html.parser')
    parsed_html.find('div')['class'] = 'relative'
    parsed_html = re.sub("(<body>|</body>|<html>|</html>)",
                         "", str(parsed_html))
    ret['menu'] = parsed_html

    # user score
    fig = user_score_bar(vendor)  # -1: ko cào dc review
    parsed_html = BeautifulSoup(plot(fig, output_type="div"), 'html.parser')
    parsed_html.find('div')['class'] = 'center2'
    parsed_html = re.sub("(<body>|</body>|<html>|</html>)",
                         "", str(parsed_html))
    ret['user_score'] = parsed_html

    # display review
    review = vendor['Reviews'].to_list()
    if pd.isnull(review[0]):
        print(1)  # nếu ko có thì ko show bảng
    else:
        review = eval(review[0])
    for i in range(len(review)):
        review[i]['Date'] = dparser.parse(
            review[i]['Date'], dayfirst=True, fuzzy=True)  # "%d/%m/%Y %H:%M"
        review[i]['Body'] = normalize_review(review[i]['Body'])
        if review[i]['User_score'] == 0:
            review[i]['User_score'] = '---'
    review = sorted(review, key=lambda d: d['Date'])
    # convert datetime back to string
    for i in range(len(review)):
        review[i]['Date'] = review[i]['Date'].strftime("%d/%m/%Y, %H:%M")

    ret['review'] = review

    # khai add filter
    ret['id'] = res_id
    filterData = []

    if request.method == 'POST':
        filterForm = request.POST.getlist('rate')

        if filterForm:
            for rate in filterForm:
                for rv in review:
                    if rv['User_score'] != '---':
                        if rate == 'Xuất sắc':
                            if float(rv['User_score']) >= 8.5:
                                filterData.append(rv)

                        elif rate == 'Tốt':
                            if float(rv['User_score']) < 8.5 and float(rv['User_score']) >= 7:
                                filterData.append(rv)

                        elif rate == 'Trung bình':
                            if float(rv['User_score']) < 7 and float(rv['User_score']) >= 5:
                                filterData.append(rv)

                        else:
                            if float(rv['User_score']) < 5:
                                filterData.append(rv)

            ret['review'] = filterData
            render(request, 'dashboard.html', ret)

    return render(request, 'dashboard.html', ret)
