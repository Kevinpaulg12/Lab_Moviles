from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ROLES = [
        ('DOCENTE', 'Docente'),
        ('ADMIN', 'Administrador'),
        ('RESPONSABLE', 'Responsable/Técnico'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='DOCENTE')
    telefono = models.CharField(max_length=20, blank=True)

    def get_tipo_display_rol(self):
        return dict(self.ROLES).get(self.rol, self.rol)