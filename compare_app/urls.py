from django.urls import path
# from .views import PriceListView
from . import views


urlpatterns = [
	path('', views.MainListView.as_view(), name = 'app-home'),
	path('contact/', views.contact, name = 'app-contact'),
	path('bootstrap/', views.BootstrapFilterView, name = 'app-bootstrap'),
	path('test/', views.HomeListView.as_view() , name = 'app-test'),
	# path('test/', views.test_table, name = 'app-test_table')
]