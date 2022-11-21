from dashboard.models import *
import csv

import sys
import csv
maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

def run():
    attributes = ['RestaurantId', 'Name', 'Address', 'District', 'City',
       'RestaurantStatus', 'Latitude', 'Longitude', 'TotalReviews',
       'nExcellentReviews', 'nGoodReviews', 'nAverageReviews', 'nBadReviews',
       'LocationScore', 'PriceScore', 'QualityScore', 'ServingScore',
       'SpaceScore', 'AvgScore', 'TotalPictures', 'TotalViews', 'TotalSaves',
       'IsBooking', 'IsDelivery', 'PrepTime', 'Capacity', 'LastHourCustomer',
       'ExtraInfo', 'Active', 'TotalFavourites', 'TotalCheckIns', 'categories',
       'cuisines', 'avg', 'service_fee', 'avg_price', 'min_order_value',
       'min_charge', 'minimum_shiping_fee', 'is_foody_delivery', 'min_price',
       'max_price', 'min_order_amount', 'expired', 'promo_description',
       'promo_code', 'max_discount_value', 'max_usage_time', 'apply_order',
       'Reviews']

    # Vendor.objects.all().delete()

    with open("dashboard/data_merge.csv", encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header
        db_vendors = {vendor.ReviewUrl: vendor for vendor in Vendor.objects.all()}
        ix = 0

        for row in reader:
            vendor_url = row[0]
            vendors_in_db = db_vendors.get(vendor_url)

            if not vendors_in_db: # nếu film chưa có trong db thì mới add
                print(ix)
                vendor = Vendor(ReviewUrl=row[0])

                for i, a in enumerate(attributes, 1):
                    try:
                        vendor.__setattr__(a, row[i])
                    except:
                        print(a)
                        shit
                
                # for field in attributes:
                #     print(f"{field}:", getattr(vendor, field))
                vendor.save()
                # shit
                db_vendors[vendor.ReviewUrl] = vendor
            ix += 1

    # with open('my_dashboard/pixar.csv') as file:
    #     reader = csv.reader(file)
    #     next(reader)  # Advance past the header

    #     Film.objects.all().delete()
    #     db_films = {film.title: film for film in Film.objects.all()}
    #     # films = []

    #     for row in reader:
    #         film_title = row[0]
    #         film_in_db = db_films.get(film_title)

    #         if not film_in_db: # nếu film chưa có trong db thì mới add
    #             print(row)
    #             film = Film(title=row[0],
    #                         year=row[2])
    #             film.save()
    #             db_films[film.title] = film
                
                