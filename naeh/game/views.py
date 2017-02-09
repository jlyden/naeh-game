# game/views.py

from django.shortcuts import get_object_or_404, render
from django.conf import settings

from .models import Game


def index(request):
    current_games = Game.objects.all()
    if not current_games:
        context = {}
    else:
        context = {'current_games': current_games}
    return render(request, 'game/index.html', context)


def get_game(request, game_id):
    this_game = get_object_or_404(Game, pk=game_id)
    return render(request, 'game/game.html', {'this_game': this_game})


def new(request):
    this_game = Game.objects.create(
        emergency_board=settings.EMERGENCY_START,
        rapid_rehousing_board=settings.RAPID_REHOUSING_START,
        outreach_board=settings.OUTREACH_START,
        transitional_board=settings.TRANSITIONAL_START,
        permanent_support_board=settings.PERMANENT_SUPPORT_START,
        available_beads=settings.AVAILABLE_BEADS
    )
    return render(request, 'game/start.html', {'this_game': this_game})
