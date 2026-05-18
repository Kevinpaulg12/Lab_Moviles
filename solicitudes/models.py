from django.db import models
from django.conf import settings


class Carrera(models.Model):
    nombre = models.CharField(max_length=100)
    facultad = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} ({self.facultad})"

    class Meta:
        ordering = ['nombre']


class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='materias')

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']


class Curso(models.Model):
    nombre = models.CharField(max_length=50)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='cursos')

    def __str__(self):
        return f"{self.materia.nombre} - {self.nombre}"

    class Meta:
        ordering = ['nombre']


class DocenteCarrera(models.Model):
    docente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='docente_carreras'
    )
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.docente.username} - {self.carrera.nombre}"

    class Meta:
        unique_together = ['docente', 'carrera']


class DocenteMateria(models.Model):
    docente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='docente_materias'
    )
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.docente.username} - {self.materia.nombre}"

    class Meta:
        unique_together = ['docente', 'materia', 'carrera', 'curso']


class Solicitud(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    docente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes'
    )
    carrera = models.ForeignKey(Carrera, on_delete=models.PROTECT)
    materia = models.ForeignKey(Materia, on_delete=models.PROTECT)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)
    bloque = models.CharField(max_length=50)
    numero_aula = models.CharField(max_length=20)
    cantidad_equipos = models.PositiveIntegerField()
    telefono_docente = models.CharField(max_length=20, default='', help_text="Teléfono de contacto del docente")
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    observaciones = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Solicitud #{self.id} - {self.docente.username} - {self.materia.nombre}"

    class Meta:
        ordering = ['-creado_en']


class Asignacion(models.Model):
    ESTADOS = [
        ('ASIGNADO', 'Asignado'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    ]

    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='asignaciones')
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='asignaciones'
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ASIGNADO')
    observaciones = models.TextField(blank=True)
    asignado_en = models.DateTimeField(auto_now_add=True)
    completado_en = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Asignación #{self.id} - Solicitud #{self.solicitud.id} - {self.responsable.username}"

    class Meta:
        ordering = ['-asignado_en']