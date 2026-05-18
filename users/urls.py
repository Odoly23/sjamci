from django.urls import path
from . import views
urlpatterns = [
	path('Profile/Utilizador/',views.UserProfile, name="UserProfile"),
	path('profile/update/',   views.update_profile_ajax, name='update_profile_ajax'),
	path('profile/photo/', views.update_photo_ajax, name='update_photo_ajax'),
	path('profile/account/',  views.manage_account_ajax, name='manage_account_ajax'),
]