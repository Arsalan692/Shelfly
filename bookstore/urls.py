from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('order/<int:book_id>/', views.place_order, name='place_order'),
    path('orders/', views.order_history, name='order_history'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact, name='contact'),
]
