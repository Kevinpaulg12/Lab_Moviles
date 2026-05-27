from django.contrib import admin
from .models import (
    Carrera, Materia, Curso, DocenteCarrera, DocenteMateria,
    Solicitud, Asignacion
)


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'facultad')
    search_fields = ('nombre', 'facultad')
    ordering = ('nombre',)


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'carrera')
    list_filter = ('carrera',)
    search_fields = ('nombre',)
    ordering = ('carrera', 'nombre')


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'materia')
    list_filter = ('materia',)
    search_fields = ('nombre',)
    ordering = ('materia', 'nombre')


@admin.register(DocenteCarrera)
class DocenteCarreraAdmin(admin.ModelAdmin):
    list_display = ('docente', 'carrera')
    list_filter = ('carrera',)
    search_fields = ('docente__username', 'carrera__nombre')


@admin.register(DocenteMateria)
class DocenteMateriaAdmin(admin.ModelAdmin):
    list_display = ('docente', 'materia', 'carrera', 'curso')
    list_filter = ('carrera', 'materia')
    search_fields = ('docente__username', 'materia__nombre')


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ('id', 'docente', 'carrera', 'materia', 'estado', 'fecha', 'creado_en')
    list_filter = ('estado', 'carrera', 'materia', 'fecha')
    search_fields = ('docente__username', 'materia__nombre')
    ordering = ('-creado_en',)
    date_hierarchy = 'creado_en'
    readonly_fields = ('creado_en', 'actualizado_en')


@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitud', 'responsable', 'estado', 'asignado_en', 'completado_en')
    list_filter = ('estado',)
    search_fields = ('responsable__username', 'solicitud__id')
    ordering = ('-asignado_en',)
    readonly_fields = ('asignado_en',)