from django.urls import path
from . import views

urlpatterns = [
    path('logout/', views.user_logout, name='logout'),
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('quote/<int:product_id>/', views.quote_form, name='quote_form'),
    path('quote/<int:product_id>/submit/', views.quote_submit, name='quote_submit'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('about/', views.about, name='about'),
    path('security/', views.security_checklist, name='security_checklist'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/phones/', views.dashboard_phones, name='dashboard_phones'),
    path('dashboard/categories/', views.dashboard_categories, name='dashboard_categories'),
    path('dashboard/add/', views.dashboard_add_product, name='dashboard_add_product'),
    path('dashboard/edit/<int:product_id>/', views.dashboard_edit_product, name='dashboard_edit_product'),
    path('dashboard/delete/<int:product_id>/', views.dashboard_delete_product, name='dashboard_delete_product'),
    path('dashboard/manage/<int:product_id>/', views.dashboard_manage, name='dashboard_manage'),
    path('dashboard/report/', views.dashboard_report, name='dashboard_report'),
    path('dashboard/reviews/', views.dashboard_reviews, name='dashboard_reviews'),
    path('dashboard/api/views-data/', views.dashboard_views_data, name='dashboard_views_data'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('product/<int:product_id>/review/', views.submit_review, name='submit_review'),
]
