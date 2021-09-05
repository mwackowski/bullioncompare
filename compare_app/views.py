from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import inlineformset_factory
from .filters import PriceFilter
from .forms import InputForm

from .models import *

pricings.objects.annotate(PRICE_PER_OZ_ORDERED=Cast('PRICE_PER_OZ', IntegerField())).order_by('PRICE_PER_OZ_ORDERED', 'PRICE_PER_OZ')



def contact(request):
	return render(request, 'compare_app/contact.html', {'title': 'Strona kontaktowa'})

def is_valid_queryparameter(param):
	return param != '' and param is not None

class MainListView(ListView):
	model = pricings

	template_name = 'compare_app/forms.html'
    
	# def get_context_data(self, **kwargs):
	# 	context = super().get_context_data(**kwargs)
	# 	context['filter'] = PriceFilter(self.request.GET, queryset=self.get_queryset())

	# 	return context
	def get(self, request):
		qs = pricings.objects.all().order_by('PRICE') #.annotate(num_notes=Count('note'))
		price_filter = PriceFilter(request.GET, queryset=qs)
		page = request.GET.get('page')
		paginator = Paginator(price_filter.qs, 10)	
		try:
			prices = paginator.page(page)
		except PageNotAnInteger:
			prices = paginator.page(1)
		except EmptyPage:
			prices = paginator.page(paginator.num_pages)

		index = paginator.page_range.index(prices.number)
		max_index = len(paginator.page_range)
		start_index = index - 5 if index >= 5 else 0
		end_index = index + 5 if index <= max_index - 5 else max_index
		page_range = paginator.page_range[start_index:end_index]

		records_page_obj = paginator.get_page(page)
		return render(request, self.template_name, {
			'prices': prices,
			'filter': price_filter.form,
			'page_range': page_range,
			'queryset': records_page_obj #price_filter.qs
		})

def BootstrapFilterView(request):

	weight_dict = {
	'one_tenth_oz': 0.1,
	'half_oz': 0.5,
	'quarter_oz': 0.25,
	'one_oz': 1,
	'two_oz': 2,
	'five_oz': 5,
	}

	qs = pricings.objects.all().order_by('PRICE')
	qs2 = pricings.objects.all().order_by('PRICE')

	filter_by_name = request.GET.get('filter_by_name')
	id_exact_query = request.GET.get('filter_by_all')
	filter_by_shop = request.GET.get('filter_by_shop')
	one_oz = request.GET.get('one_oz')
	half_oz = request.GET.get('half_oz')
	one_tenth_oz = request.GET.get('one_tenth_oz')
	quarter_oz = request.GET.get('quarter_oz')
	two_oz = request.GET.get('two_oz')
	five_oz = request.GET.get('five_oz')

	if(request.GET.get('btn_order_name')):
		qs = pricings.objects.all().order_by('NAME')

	if(request.GET.get('btn_order_peroz')):
		qs = pricings.objects.all().order_by('PRICE_PER_OZ')

	if(request.GET.get('btn_order_price')):
		qs = pricings.objects.all().order_by('PRICE')

	if is_valid_queryparameter(filter_by_name):
		qs = qs.filter(NAME__icontains=filter_by_name)

	elif is_valid_queryparameter(id_exact_query):
		qs = qs.filter(id=id_exact_query)	

	if is_valid_queryparameter(filter_by_shop):
		shop_dict = {'GoldSilver.be': 'GoldSilver',
		'Europeanmint.com': 'EuropeanMint',
		'Srebrnamennica.pl': 'SrebrnaMennica',
		}
		if filter_by_shop in shop_dict:
			filter_parameter = shop_dict[filter_by_shop]
		else: 
			filter_parameter = ''
		qs = qs.filter(SHOP__icontains = filter_parameter)

	filter_list = []
	if one_oz:
		filter_list.append('1')

	if half_oz:
		filter_list.append('0.5')

	if quarter_oz:
		filter_list.append('0.25')

	if one_tenth_oz:	
		filter_list.append('0.1')

	if two_oz:
		filter_list.append('2')

	if five_oz:
		filter_list.append('5')

	if len(filter_list) != 0:
		qs = qs.filter(OZ__in = filter_list)

	
	paginated_filtered_records = Paginator(qs, 20)
	page_number = request.GET.get('page')
	records_page_obj = paginated_filtered_records.get_page(page_number)


	context = {
		'queryset': records_page_obj,
		# 'myFilter': myFilter,
	}
	return render(request, 'compare_app/main.html', context)



class HomeListView(ListView):

	model = pricings

	template_name = 'compare_app/home.html'
    

	def get(self, request):
		qs = pricings.objects.all().order_by('PRICE') #.annotate(num_notes=Count('note'))
		price_filter = PriceFilter(request.GET, queryset=qs)
		page = request.GET.get('page')
		paginator = Paginator(price_filter.qs, 10)	
		try:
			prices = paginator.page(page)
		except PageNotAnInteger:
			prices = paginator.page(1)
		except EmptyPage:
			prices = paginator.page(paginator.num_pages)

		index = paginator.page_range.index(prices.number)
		max_index = len(paginator.page_range)
		start_index = index - 5 if index >= 5 else 0
		end_index = index + 5 if index <= max_index - 5 else max_index
		page_range = paginator.page_range[start_index:end_index]

		records_page_obj = paginator.get_page(page)
		return render(request, self.template_name, {
			'prices': prices,
			'filter': price_filter.form,
			'page_range': page_range,
			'queryset': records_page_obj #price_filter.qs
		})