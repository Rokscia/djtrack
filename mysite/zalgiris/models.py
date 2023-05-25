from django.db import models


class GameScore(models.Model):
    game_date = models.DateField(auto_now=False, auto_now_add=False)
    zalgiris_score = models.IntegerField(blank=True)
    barcelona_score = models.IntegerField(blank=True)

    def __str__(self):
        return str(self.game_date)


class Totalizator(models.Model):
    name = models.CharField(max_length=100, unique=True)
    zalgiris_guess = models.IntegerField()
    barcelona_guess = models.IntegerField()
    guess_accuracy = models.FloatField(null=True)
    game_score = models.ForeignKey(
        GameScore, on_delete=models.SET_NULL, blank=True, null=True)
