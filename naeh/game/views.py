# game/views.py

from django.shortcuts import get_object_or_404, render
from django.conf import settings

from utils import get_random_bead
from .models import Game


def index(request):
    current_games = Game.objects.all()
    if not current_games:
        context = {}
    else:
        context = {'current_games': current_games}
    return render(request, 'game/index.html', context)


def status(request, game_id):
    this_game = get_object_or_404(Game, pk=game_id)
    return render(request, 'game/status.html', {'this_game': this_game})


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


def load_intake(request, game_id):
    this_game = get_object_or_404(Game, pk=game_id)
    error_message = ''

    # Validation: Only load intake board after end of previous round
    if not this_game.round_over:
        error_message = "Only fill intake board once per round."
    elif this_game.intake_board:
        error_message = "Your intake board is already full!"
    # If already at round 5, round 6 would be started by load_intake
    elif this_game.round_count > 4:
        error_message = "Game is already over!"
    else:
        collection, this_game.available_beads = get_random_bead(
            50, this_game.available_beads)
        this_game.intake_board = collection

        # Now the round has begun, so up-counter and toggle flag
        this_game.round_count += 1
        this_game.round_over = False
        this_game.save()

    if error_message:
        return render(request, 'game/status.html', {
                      'this_game': this_game, 'error_message': error_message,
                      })
    else:
        return render(request, 'game/status.html', {'this_game': this_game})
