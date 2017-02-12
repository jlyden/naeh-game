# game/models.py

from __future__ import unicode_literals

from django.db import models
from django.core.validators import validate_comma_separated_integer_list
from django.urls import reverse


class Game(models.Model):
    round_count = models.IntegerField(default=0)
    round_over = models.BooleanField(default=False)
    diversion = models.BooleanField(default=False)

    available_beads = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=2000)
    market_housing = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=2000,
        default=0)
    unsheltered_homeless = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=2000,
        default=0)

    intake_board = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2000)
    emergency_board = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2000)
    rapid_rehousing_board = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2000)
    outreach_board = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2000)
    transitional_board = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2000)
    permanent_support_board = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2000)

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return "/game/%i" % self.id
#        return reverse('detail', args=[self.id])


class Score(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    emergency_count = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=35)
    transitional_count = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=35)
