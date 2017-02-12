# game/models.py

from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.core.validators import validate_comma_separated_integer_list
from django.urls import reverse


class Game(models.Model):
    round_count = models.IntegerField(default=0)
    round_over = models.BooleanField(default=True)
    diversion = models.BooleanField(default=False)

    available_beads = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=2000,
        default=settings.AVAILABLE_BEADS)
    market_housing = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=2000,
        default='')
    unsheltered_homeless = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=2000,
        default='')

    intake_board = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=2000,
        default='')
    emergency_board = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=2000,
        default=settings.EMERGENCY_START)
    rapid_rehousing_board = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=2000,
        default=settings.RAPID_REHOUSING_START)
    outreach_board = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=2000,
        default=settings.OUTREACH_START)
    transitional_board = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=2000,
        default=settings.TRANSITIONAL_START)
    permanent_support_board = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=2000,
        default=settings.PERMANENT_SUPPORT_START)

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('game:status', args=[self.id])


class Score(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    emergency_count = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=35)
    transitional_count = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=35)
