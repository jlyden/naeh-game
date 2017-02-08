# game/views.py

from django.http import Http404
from django.shortcuts import render

from .models import Game


def index(request):
    current_games = Game.objects.all()
    if not current_games:
        context = {}
    else:
        context = {'current_games': current_games}
    return render(request, 'game/index.html', context)


def game(request, game_id):
    try:
        this_game = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        raise Http404("That game does not exist.")
    return render(request, 'game/game.html', {'this_game': this_game})


def new(request):
    this_game = Game.new_game()
    return render(request, 'game/game.html', {'this_game': this_game})
