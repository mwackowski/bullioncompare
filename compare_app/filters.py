import django_filters
from django_filters import CharFilter
from django.forms import fields
from django import forms
# from crispy_forms.helper import FormHelper
from .models import *

class PriceFilter(django_filters.FilterSet):



    CHOICES = (
        ('price', 'Cena'),
        # ('price_per_oz', 'Cena/oz'),
        ('name', 'Nazwa')
    )
    OZ = (
        ('0.1', '1/10 oz'),
        ('0.25', '1/4 oz'),
        ('0.5', '1/2 oz'),
        ('1', '1 oz', ),
        ( '2', '2 oz'),
        ( '5', '5 oz'),
        ( '10', '10 oz'),
        ('0', 'inne')
        )
    SHOPS = (( 'GoldSilver', 'GoldSilver.be'),
		('EuropeanMint', 'Europeanmint.com'),
		('SrebrnaMennica','SrebrnaMennica.pl'),
		('SzlachetneInwestycje', 'SzlachetneInwestycje.pl'),
        ('MetalMarket','MetalMarket.eu'),
        ('Goldon', 'Goldon.pl'),
        ('Silbertresor', 'Silbertresor.de'),
        ('Emk', 'Emk.com'),
        ('79thElement', '79element.pl'),
		)

    METALS = (('Silver', 'Srebro'), ('Gold', 'Złoto'))


    NAME = django_filters.CharFilter(label="Filter by name", lookup_expr='icontains', widget=forms.TextInput(
        attrs={ 'class': 'form-control',
                'placeholder': 'Wpisz szukaną frazę'
        }
    ))   #( label = "Filtruj po nazwie", method = 'filter_by_name')


    shop_filter = django_filters.ChoiceFilter(label="Filter by shop", choices = SHOPS,
    method = 'filter_by_shop', widget=forms.Select(
        attrs={ 'class': 'form-control'
        }
    ))

    ordering = django_filters.ChoiceFilter(label="Sortuj wg", choices = CHOICES,
    method = 'filter_by_order', widget=forms.Select(
        attrs={ 'class': 'form-control'
        }
    ))

    metals = django_filters.ChoiceFilter(
        label = "Filter by weight",
        required=False,
        choices=METALS,
        method = 'filter_by_metal',
        widget=forms.Select(
        attrs={ 'class': 'form-control'        }
    )
    )

    weights = django_filters.MultipleChoiceFilter(
        label = "Filter by weight",
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class' : 'weightCheckboxes'}),
        choices=OZ,
        method = 'filter_by_weight'

    )


    class Meta:
        model = pricings
        fields = [] #{'NAME': ['icontains']}
        # fields = {'NAME': ['icontains'],
        # # 'WEIGHT': ['icontains'],
        # # 'PRICE': ['iexact'],
        # # 'PRICE_PER_OZ': ['iexact']

        # }

    def filter_by_Name(self, qs, name, value):
        return qs.filter(NAME__icontains = value)

    def filter_by_shop(self, qs, name, value):
        return qs.filter(SHOP__icontains = value)

    def filter_by_weight(self, qs, name, value):
        print(value)
        if len(value) != 0:
            if value != '0':
                qs = qs.filter(OZ__in = value)
            else:
                qs = qs.exclude(OZ_in=['0.1', '0.25', '0.5', '1', '2','5','10'])
            return qs

    def filter_by_metal(self, qs, name, value):
        return qs.filter(METAL__icontains = value)

    def filter_by_order(self, qs, name, value):
        if value == 'price':
            expression = 'PRICE'
        elif value == 'price_per_oz':
            # expression = 'PRICE_PER_OZ_ORDERED'
            expression = 'PRICE_PER_OZ'
        else: expression = 'NAME'
        return qs.order_by(expression)

    def __init__(self, *args, **kwargs):
        super(PriceFilter, self).__init__(*args, **kwargs)
        # self.filters['NAME__icontains'].label="Filtruj po nazwie"