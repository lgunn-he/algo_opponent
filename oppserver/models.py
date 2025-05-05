from django.db import models

class GameData(models.Model):
  board_height = models.FloatField()
  board_width = models.FloatField()
  game_mode = models.CharField(max_length=6)
  hPadHeight = models.FloatField()
  movement = models.FloatField()
  last_update = models.IntegerField()
