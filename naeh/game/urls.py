# game/urls.py
from django.conf.urls import url

from . import views

app_name = 'game'
urlpatterns = [
    # ex: /game/
    url(r'^$', views.index, name='index'),
    # ex: /game/6/
    url(r'^(?P<game_id>[0-9]+)/$', views.get_game, name='get_game'),
    # ex: /game/new/
    url(r'^new/', views.new, name='new'),
]
