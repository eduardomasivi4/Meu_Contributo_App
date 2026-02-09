from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Atividade(models.Model):
    TIPO_CHOICES = [
        ('Acadêmica', 'Acadêmica'),
        ('Projeto', 'Projeto'),
        ('Voluntariado', 'Voluntariado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    creditos = models.IntegerField()
    data = models.DateField()
    descricao = models.TextField()

    def __str__(self):
        return self.nome
