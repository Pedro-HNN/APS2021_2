from django.db import models

LEVELS = (
        (1,"Usuário"),
        (2,"Admin"),
        (3,"Dono")
    )

# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, unique=True)
    level = models.IntegerField(choices=LEVELS)

    def __str__(self):
        return self.name

    def get_level(self):
        return (LEVELS[int(self.level)-1])[1]
