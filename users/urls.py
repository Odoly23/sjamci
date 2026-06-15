from django.urls import path
from . import views

urlpatterns = [
	path('Profile/Utilizador/',views.UserProfile, name="UserProfile"),
	path('profile/update/',   views.update_profile_ajax, name='update_profile_ajax'),
	path('profile/photo/', views.update_photo_ajax, name='update_photo_ajax'),
	path('profile/account/',  views.manage_account_ajax, name='manage_account_ajax'),


	#benefisiariu Users
    path("benefisiariu-user/", views.benefisiariu_user_list, name="benefisiariu-user-list"),
    path("benefisiariu-user/edit/<int:pk>/", views.benefisiariu_user_edit, name="benefisiariu-user-edit"),
    path("benefisiariu-user/delete/<int:pk>/", views.benefisiariu_user_delete, name="benefisiariu-user-delete"),

    path('list/', views.PList, name="u-list"),
    path('add/', views.EmpAdd, name="user-add"),
    path('emp/<str:pk>/', views.emp_detail,  name='emp-detail'),
    path('emp/<str:pk>/update/',    views.emp_update,           name='emp-update'),
    path('emp/<str:pk>/position/',  views.empposition_update,   name='empposition-update'),
    path('emp/<str:pk>/division/',  views.empdivision_update,   name='empdivision-update'),

]