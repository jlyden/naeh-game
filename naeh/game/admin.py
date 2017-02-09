# game/admin.py
from django.contrib import admin

from .models import Game
from .models import Score

# Register your models here.
admin.site.register(Game)
admin.site.register(Score)
