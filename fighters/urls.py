from django.urls import path
from . import views

app_name = 'fighters'
urlpatterns = [
    path('', views.fighter_list, name='fighter_list'),
    path('fighter/<int:pk>/', views.fighter_detail, name='fighter_detail'),
    path('search/', views.search_fighters, name='search'),
    path('fighters/compare/', views.compare_fighters, name='compare'),
    path('fighters/autocomplete/', views.autocomplete, name='autocomplete'),
    path('countdown/', views.countdown_view, name='countdown'),
    path('poll/<int:fight_id>/', views.poll_view, name='poll'),
    path('polls/', views.poll_list_view, name='poll_list'),
]