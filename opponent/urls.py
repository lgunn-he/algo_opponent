from django.contrib import admin
from django.urls import path
from oppserver.views import calc_move
from oppserver.views import manage_games

urlpatterns = [
    path('calc/', calc_move, name='calc_move'),
    path('manage/', manage_games, name='manage_games'),
]
