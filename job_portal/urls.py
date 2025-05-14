from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('my-applications/<int:application_id>/withdraw/', views.withdraw_application, name='withdraw_application'),
    path('api/applications/<int:application_id>/', views.application_details_api, name='application_details_api'),
    path('contact/', views.contact_support, name='contact_support'),
] 