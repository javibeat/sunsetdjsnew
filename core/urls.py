from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('calendar/', views.global_calendar, name='global_calendar'),
    path('calendar/<int:dj_id>/', views.dj_calendar, name='dj_calendar'),
    path('login/', views.login_view, name='login'),
    path('verify/<str:token>/', views.verify_token_view, name='verify_token'),
    path('dj/<int:dj_id>/dashboard/', views.dj_dashboard_view, name='dj_dashboard'),
    path('insert/', views.insert_shift_view, name='insert_shift'),
    path('delete_shift/<int:shift_id>/', views.delete_shift_view, name='delete_shift'),
    path('get_dj_summary/', views.get_dj_summary_view, name='get_dj_summary'),
]