# game/models.py

from __future__ import unicode_literals

from django.db import models
from django.core.validators import validate_comma_separated_integer_list
from django.conf import settings


class Game(models.Model):
    turn = models.IntegerField(default=0)
    diversion = models.BooleanField(default=False)

    available_beads = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=1000)
    market_housing = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=1000,
        default=0)
    unsheltered_homeless = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=1000,
        default=0)

    intake_board = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=1000)
    emergency_board = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=1000)
    rapid_rehousing_board = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=1000)
    outreach_board = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=1000)
    transitional_board = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=1000)
    permanent_support_board = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=1000)

    def __str__(self):
        return self.id

    def new_game():
        game = Game(
            emergency_board=settings.EMERGENCY_START,
            rapid_rehousing_board=settings.RAPID_REHOUSING_START,
            outreach_board=settings.OUTREACH_START,
            transitional_board=settings.TRANSITIONAL_START,
            permanent_support_board=settings.PERMANENT_SUPPORT_START,
            available_beads=settings.AVAILABLE_BEADS)
        game.save()
        return game


class Score(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    emergency_count = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=35)
    transitional_count = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=35)
