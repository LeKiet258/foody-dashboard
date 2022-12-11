from django.http import HttpResponse
from django.shortcuts import render, redirect
from dashboard.models import Vendor
import numpy as np

cuisines_list = ['Bánh Pizza', 'Hà Nội', 'Miền Đông', 'Campuchia', 'Tây Ban Nha', 'Mỹ', 'Pháp', 'Nam Định', 'Đài Loan', 'Tây Bắc', 'Á', 'Úc', 'Âu', 'Đặc biệt', 'Đặc sản vùng', 'Đức', 'Buôn Mê', 'Iran', 'Châu Phi', 'Bắc Âu', 'Ý', 'Mexico', 'Đà Lạt', 'Philippines', 'Bình Định', 'Ấn Độ', 'Canada', 'Miền Nam', 'Tiệp (Séc)', 'Malaysia', 'Trung Đông', 'Quốc tế', 'Hàn', 'Nha Trang', 'Thổ Nhĩ Kỳ', 'Đông Âu', 'Brazil', 'Việt', 'Quảng', 'Thái', 'Ả Rập', 'Nhật', 'Miền Tây', 'Tây Nguyên', 'Bắc', 'Trung Hoa', 'Huế', 'Singapore', 'Miền Trung', 'Châu Mỹ']
districts_list = ['Quận 1', 'Quận 3', 'Quận Phú Nhuận', 'Quận 5', 'Quận Tân Bình', 'Quận Bình Thạnh', 'Quận 11', 'Quận 10','Quận Tân Phú', 'Quận Bình Tân', 'Quận 8', 'Quận Gò Vấp', 'Quận 4', 'Tp. Thủ Đức', 'Quận 7', 'Quận 9', 'Quận 6', 'Quận 2','Huyện Nhà Bè', 'Quận 12', 'Huyện Hóc Môn', 'Huyện Bình Chánh', 'Huyện Củ Chi'] 
# Create your views here.


def search(request):
    context = {}
    if request.method == 'POST':
        search = request.POST.get('search')

        vendors = Vendor.objects.all()

        finalVendors = []
        for vendor in vendors:
            if search.lower() in vendor.Name.lower():
                finalVendors.append(vendor)

        context = {'vendors': finalVendors}
        # sử lý sự kiên search

        if len(finalVendors) == 0:
            return render(request, 'search/emptyPage.html', context)

        return render(request, 'search/searchResult.html', context)

    return render(request, 'search/searchPage.html', context)


def filter(request):
    filterData = []
    if request.method == 'POST':
        districts = request.POST.getlist('districts')
        cuisines = request.POST.getlist('cuisines')
        if districts:
            filterData = Vendor.objects.filter(District__in=districts)

        if cuisines:
            finalVendor = []
            vendors = Vendor.objects.all()
            for vendor in vendors:
                finalCuisines = []
                temp = vendor.cuisines[1:len(vendor.cuisines)-1].split(", ")
                for t in temp:
                    t = t[1:len(t)-1].split('Món ')[-1]
                    finalCuisines.append(t)

                if np.in1d(finalCuisines, cuisines).any():
                    finalVendor.append(vendor)
            filterData = finalVendor

        for r in range(len(filterData)):
            cui = ''
            temp = filterData[r].cuisines[1:len(filterData[r].cuisines)-1].split(", ")
            for t in temp:
                t = t[1:len(t)-1].split('Món ')[-1]
                cui += t + ', '
            filterData[r].cuisines = cui[:-2]

            filterData[r].AvgScore = round(filterData[r].AvgScore, 1)

            filterData[r].min_price = int(filterData[r].min_price)
            filterData[r].max_price = int(filterData[r].max_price)
            filterData[r].TotalViews = int(filterData[r].TotalViews)
            if filterData[r].seeding_pct == '':
                filterData[r].seeding_pct = 0
            elif filterData[r].seeding_pct == '1.00':
                filterData[r].seeding_pct = 100
            else:
                if len(filterData[r].seeding_pct.split('.')[1]) == 1:
                    filterData[r].seeding_pct = int(filterData[r].seeding_pct.split('.')[1])*10
                else:
                    filterData[r].seeding_pct = int(filterData[r].seeding_pct.split('.')[1])

        return render(request, 'smallfood.html', {'page_obj': filterData, 'cuisines': cuisines_list, 'districts': districts_list})

    return render(request, 'smallfood.html', {'page_obj': filterData, 'cuisines': cuisines_list, 'districts': districts_list})
