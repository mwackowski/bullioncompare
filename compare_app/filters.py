import django_filters
from django_filters import CharFilter
from django.forms import fields
from django import forms
# from crispy_forms.helper import FormHelper
from .models import *

class PriceFilter(django_filters.FilterSet):

    

    CHOICES = (
        ('price', 'Cena'),
        ('price_per_oz', 'Cena/oz'),
        ('name', 'Nazwa')
    )
    OZ = (
        ('1', '1 oz', ), ( '2', '2 oz'), ( '5', '5 oz')
        )
    SHOPS = (( 'GoldSilver', 'GoldSilver.be'),
		('EuropeanMint', 'Europeanmint.com'),
		('SrebrnaMennica','Srebrnamennica.pl')
		)
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


    weights = django_filters.MultipleChoiceFilter(
        label = "Filter by weight",
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class' : 'weightCheckboxes'}),
        choices=OZ,
        method = 'filter_by_checkbox'
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
        print(value)
        return qs.filter(SHOP__icontains = value)

    def filter_by_checkbox(self, qs, name, value):

        if len(value) != 0:
            qs = qs.filter(OZ__in = value)
            return qs
        
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


# class OtherFilter(django_filters.FilterSet):
#     def __init__(self, *args, **kwargs):
#             super(OtherFilter, self).__init__(*args, **kwargs)
#             self.filters['NAME__icontains'].label="Filtruj po nazwie"

#     OZ = (
#         ('1', '1 oz', ), ( '2', '2 oz'), ( '5', '5 oz')
#         )

#     favorite_colors = django_filters.MultipleChoiceFilter(
#         label = "Filtruj wg wagi",
#         required=False,
#         widget=forms.CheckboxSelectMultiple,
#         choices=OZ,
#         method = 'filter_by_checkbox'
#     )
    

#     class Meta:
#         model = pricings
#         fields = {'NAME': ['icontains']}

#     def filter_by_checkbox(self, qs, name, value):

#         if len(value) != 0:
#             qs = qs.filter(OZ__in = value)
#             return qs
        
