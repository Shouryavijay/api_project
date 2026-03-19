from django.urls import path
from .views import (
    health_check,
    register,
    me,
    note_list_create,
    note_detail,
    ProductListCreateView,
    ProductDetailView,
    OrderListCreateView,
    OrderDetailView,
)

urlpatterns = [
    path('health/', health_check),
    path('register/', register),
    path('me/', me),
    path('notes/', note_list_create),
    path('notes/<int:pk>/', note_detail),
    path('products/', ProductListCreateView.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view()),
    path('orders/', OrderListCreateView.as_view()),
    path('orders/<int:pk>/', OrderDetailView.as_view()),
]
