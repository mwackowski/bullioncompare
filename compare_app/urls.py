from django.urls import path
# from .views import PriceListView
from . import views


urlpatterns = [
	path('', views.home, name = 'app-home'),
	path('contact/', views.contact, name = 'app-contact'),
	path('bootstrap/', views.BootstrapFilterView, name = 'app-bootstrap'),
	path('filter/', views.MainListView.as_view(), name = 'app-pricelist'),
	# path('test/', views.test_table, name = 'app-test_table')
]