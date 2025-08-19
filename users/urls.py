from django.urls import path
from . import views

urlpatterns = [
	path('signup/', views.SignUp.as_view(), name='signup'),
	path('login/', views.CustomLoginView.as_view(), name='login'),
	path('profile/', views.ProfileView.as_view(), name='profile'),
]
