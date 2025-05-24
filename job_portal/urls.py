from django.urls import path, include
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
    
    # Social Auth URLs - handle both authentication and callback
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('oauth/', views.handle_auth_callback, name='auth_callback'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-jobs/', views.manage_jobs, name='manage_jobs'),
    path('create-job/', views.create_job, name='create_job'),
    path('edit-job/<int:job_id>/', views.edit_job, name='edit_job'),
    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),
    path('job/<int:job_id>/applications/', views.job_applications, name='job_applications'),
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),
    path('application/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    path('manage-applications/', views.manage_applications, name='manage_applications'),
    path('support-tickets/', views.support_tickets, name='support_tickets'),
] 