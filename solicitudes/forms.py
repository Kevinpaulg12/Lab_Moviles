from django import forms
from .models import Solicitud, Asignacion, Carrera, Materia, Curso


class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = [
            'carrera', 'materia', 'curso',
            'bloque', 'numero_aula', 'cantidad_equipos', 'telefono_docente',
            'fecha', 'hora_inicio', 'hora_fin', 'descripcion'
        ]
        widgets = {
            'carrera': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 outline-none bg-white'
            }),
            'materia': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 outline-none bg-white'
            }),
            'curso': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 outline-none bg-white'
            }),
            'bloque': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 outline-none',
                'placeholder': 'Ej: Bloque A, Bloque B'
            }),
            'numero_aula': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 outline-none',
                'placeholder': 'Ej: 101, LAB-1'
            }),
            'cantidad_equipos': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 outline-none',
                'placeholder': 'Cantidad de equipos requeridos',
                'min': '1'
            }),
            'telefono_docente': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 outline-none',
                'placeholder': 'Ej: 0991234567'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 outline-none',
                'type': 'date'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 outline-none',
                'type': 'time'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 outline-none',
                'type': 'time'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 outline-none',
                'placeholder': 'Descripción adicional de la práctica (opcional)',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        docente = kwargs.pop('docente', None)
        super().__init__(*args, **kwargs)
        
        if docente:
            # Cargar todas las opciones disponibles
            carrera_ids = docente.docente_carreras.values_list('carrera_id', flat=True)
            self.fields['carrera'].queryset = Carrera.objects.filter(id__in=carrera_ids)
            # Permitir todas las materias y cursos
            self.fields['materia'].queryset = Materia.objects.all()
            self.fields['curso'].queryset = Curso.objects.all()


class AsignacionForm(forms.ModelForm):
    class Meta:
        model = Asignacion
        fields = ['responsable', 'observaciones']
        widgets = {
            'responsable': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 outline-none bg-white'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 outline-none',
                'placeholder': 'Observaciones (opcional)',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import Usuario
        self.fields['responsable'].queryset = Usuario.objects.filter(rol='RESPONSABLE')