from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.RegisterAPI.as_view(),name='register'),
    path('login/',views.LoginAPI.as_view(),name='login'),
    path('logout/',views.LogoutAPI.as_view(),name='logout'),
    path('forgot-password/',views.ForgotPasswordAPI.as_view(),name='forgot-password'),
    path('notifications/',views.NotificationAPI.as_view(),name='notifications'),
    path('food/',views.FoodAPI.as_view(),name='food'),
    path('cart/',views.CartAPI.as_view(),name='cart'),
    path('cart/<int:pk>/',views.CartItemAPI.as_view(),name='cart-detail'),
    path('order/',views.OrderAPI.as_view(),name='order'),
    path('order/<int:pk>/',views.OrderDetailAPI.as_view(),name='order-detail'),
    path('search/',views.SearchAndFilterAPI.as_view(),name='search'),
    path('provider-orders/',views.ProviderOrderAPI.as_view(),name='provider-orders'),
    path('recommendations/',views.get_food_recommendations,name='recommendations'),
]