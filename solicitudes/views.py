from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Solicitud, Asignacion, DocenteCarrera, DocenteMateria, Carrera, Materia, Curso, SolicitudEspecial
from .forms import SolicitudForm, AsignacionForm, SolicitudEspecialForm
from accounts.models import Usuario


def home(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if request.user.rol == 'ADMIN':
        pendientes = (
            Solicitud.objects.filter(estado='PENDIENTE').count() +
            SolicitudEspecial.objects.filter(estado='PENDIENTE').count()
        )
        aprobadas = (
            Solicitud.objects.filter(estado='APROBADA').count() +
            SolicitudEspecial.objects.filter(estado='APROBADA').count()
        )
        rechazadas = (
            Solicitud.objects.filter(estado='RECHAZADA').count() +
            SolicitudEspecial.objects.filter(estado='RECHAZADA').count()
        )
        return render(request, 'solicitudes/home_admin.html', {
            'pendientes': pendientes,
            'aprobadas': aprobadas,
            'rechazadas': rechazadas,
        })
    elif request.user.rol == 'RESPONSABLE':
        asignaciones_pendientes = request.user.asignaciones.filter(estado='ASIGNADO').count()
        asignaciones_completadas = request.user.asignaciones.filter(estado='COMPLETADO').count()
        return render(request, 'solicitudes/home_responsable.html', {
            'asignaciones_pendientes': asignaciones_pendientes,
            'asignaciones_completadas': asignaciones_completadas,
        })
    else:
        mis_solicitudes = request.user.solicitudes.all()[:5]
        return render(request, 'solicitudes/home_docente.html', {
            'mis_solicitudes': mis_solicitudes,
        })

@login_required
def crear_solicitud(request):
    if request.user.rol != 'DOCENTE':
        messages.error(request, 'No tienes permiso para crear solicitudes')
        return redirect('solicitudes:home')
    
    docente = request.user
    
    if request.method == 'POST':
        form = SolicitudForm(request.POST, docente=docente)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.docente = docente
            solicitud.save()
            messages.success(request, f'Solicitud #{solicitud.id} creada exitosamente')
            return redirect('solicitudes:mis_solicitudes')
        else:
            error_list = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label or field
                    error_list.append(f"{field_label}: {error}")
            messages.error(request, f"Errores en el formulario: {'; '.join(error_list)}")
    else:
        form = SolicitudForm(docente=docente)
    
    carreras_docente = docente.docente_carreras.select_related('carrera').all()
    
    return render(request, 'solicitudes/crear_solicitud.html', {
        'form': form,
        'carreras_docente': carreras_docente
    })


@login_required
def mis_solicitudes(request):
    if request.user.rol != 'DOCENTE':
        messages.error(request, 'No tienes permiso para ver solicitudes')
        return redirect('solicitudes:home')
    
    solicitudes = request.user.solicitudes.all()
    
    return render(request, 'solicitudes/mis_solicitudes.html', {
        'solicitudes': solicitudes
    })


@login_required
def lista_solicitudes(request):
    if request.user.rol != 'ADMIN':
        messages.error(request, 'No tienes permiso para ver esta página')
        return redirect('solicitudes:home')

    estado_filter = request.GET.get('estado')

    solicitudes = Solicitud.objects.select_related('docente', 'carrera', 'materia', 'curso').all()
    solicitudes_especiales = SolicitudEspecial.objects.select_related('docente', 'carrera', 'materia', 'curso').all()

    if estado_filter:
        solicitudes = solicitudes.filter(estado=estado_filter)
        solicitudes_especiales = solicitudes_especiales.filter(estado=estado_filter)

    return render(request, 'solicitudes/lista_solicitudes.html', {
        'solicitudes': solicitudes,
        'solicitudes_especiales': solicitudes_especiales,
        'estado_actual': estado_filter,
    })

@login_required
def detalle_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(
        Solicitud.objects.select_related('docente', 'carrera', 'materia', 'curso'),
        id=solicitud_id
    )
    
    if request.user.rol not in ['ADMIN', 'DOCENTE', 'RESPONSABLE']:
        messages.error(request, 'No tienes permiso para ver esta solicitud')
        return redirect('solicitudes:home')
    
    if request.user.rol == 'DOCENTE' and solicitud.docente != request.user:
        messages.error(request, 'No tienes permiso para ver esta solicitud')
        return redirect('solicitudes:mis_solicitudes')
    
    asignaciones = solicitud.asignaciones.select_related('responsable').all()
    
    return render(request, 'solicitudes/detalle_solicitud.html', {
        'solicitud': solicitud,
        'asignaciones': asignaciones
    })


@login_required
def aprobar_solicitud(request, solicitud_id):
    if request.user.rol != 'ADMIN':
        messages.error(request, 'No tienes permiso para aprobar solicitudes')
        return redirect('solicitudes:home')
    
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    if solicitud.estado != 'PENDIENTE':
        messages.error(request, 'Esta solicitud ya fue procesada')
        return redirect('solicitudes:detalle_solicitud', solicitud_id=solicitud_id)
    
    solicitud.estado = 'APROBADA'
    solicitud.save()
    messages.success(request, f'Solicitud #{solicitud.id} aprobada')
    return redirect('solicitudes:detalle_solicitud', solicitud_id=solicitud_id)


@login_required
def rechazar_solicitud(request, solicitud_id):
    if request.user.rol != 'ADMIN':
        messages.error(request, 'No tienes permiso para rechazar solicitudes')
        return redirect('solicitudes:home')
    
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    if request.method == 'POST':
        if solicitud.estado != 'PENDIENTE':
            messages.error(request, 'Esta solicitud ya fue procesada')
            return redirect('solicitudes:detalle_solicitud', solicitud_id=solicitud_id)
        
        solicitud.estado = 'RECHAZADA'
        solicitud.observaciones = request.POST.get('observaciones', '')
        solicitud.save()
        messages.success(request, f'Solicitud #{solicitud.id} rechazada')
        return redirect('solicitudes:lista_solicitudes')
    
    return render(request, 'solicitudes/rechazar_solicitud.html', {'solicitud': solicitud})


@login_required
def asignar_responsable(request, solicitud_id):
    if request.user.rol != 'ADMIN':
        messages.error(request, 'No tienes permiso para asignar responsables')
        return redirect('solicitudes:home')
    
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    if solicitud.estado != 'APROBADA':
        messages.error(request, 'Solo se pueden asignar responsables a solicitudes aprobadas')
        return redirect('solicitudes:detalle_solicitud', solicitud_id=solicitud_id)
    
    if request.method == 'POST':
        form = AsignacionForm(request.POST)
        if form.is_valid():
            asignacion = form.save(commit=False)
            asignacion.solicitud = solicitud
            asignacion.save()
            messages.success(request, f'Responsable asignado a Solicitud #{solicitud.id}')
            return redirect('solicitudes:detalle_solicitud', solicitud_id=solicitud_id)
    else:
        form = AsignacionForm()
    
    return render(request, 'solicitudes/asignar_responsable.html', {
        'form': form,
        'solicitud': solicitud
    })

@login_required
def asignar_responsable_especial(request, solicitud_id):
    if request.user.rol != 'ADMIN':
        messages.error(request, 'No tienes permiso para asignar responsables')
        return redirect('solicitudes:home')
    
    solicitud = get_object_or_404(SolicitudEspecial, id=solicitud_id)
    
    if solicitud.estado != 'APROBADA':
        messages.error(request, 'Solo se pueden asignar responsables a solicitudes aprobadas')
        return redirect('solicitudes:detalle_solicitud_especial', solicitud_id=solicitud_id)
    
    if request.method == 'POST':
        form = AsignacionForm(request.POST)
        if form.is_valid():
            asignacion = form.save(commit=False)
            asignacion.solicitud_especial = solicitud
            asignacion.save()
            messages.success(request, f'Responsable asignado a Solicitud Especial #{solicitud.id}')
            return redirect('solicitudes:detalle_solicitud_especial', solicitud_id=solicitud_id)
    else:
        form = AsignacionForm()
    
    return render(request, 'solicitudes/asignar_responsable.html', {
        'form': form,
        'solicitud': solicitud
    })

@login_required
def mis_asignaciones(request):
    if request.user.rol != 'RESPONSABLE':
        messages.error(request, 'No tienes permiso para ver esta página')
        return redirect('solicitudes:home')
    
    asignaciones = request.user.asignaciones.select_related(
        'solicitud', 'solicitud__docente', 'solicitud__carrera', 'solicitud__materia'
    ).all()
    estado_filter = request.GET.get('estado')
    
    if estado_filter:
        asignaciones = asignaciones.filter(estado=estado_filter)
    
    return render(request, 'solicitudes/mis_asignaciones.html', {
        'asignaciones': asignaciones,
        'estado_actual': estado_filter
    })


@login_required
def completar_asignacion(request, asignacion_id):
    if request.user.rol != 'RESPONSABLE':
        messages.error(request, 'No tienes permiso para completar asignaciones')
        return redirect('solicitudes:home')
    
    asignacion = get_object_or_404(Asignacion, id=asignacion_id, responsable=request.user)
    
    if asignacion.estado != 'ASIGNADO':
        messages.error(request, 'Esta asignación ya fue procesada')
        return redirect('solicitudes:mis_asignaciones')
    
    if request.method == 'POST':
        accion = request.POST.get('accion', 'COMPLETADO')
        if accion == 'COMPLETADO':
            asignacion.estado = 'COMPLETADO'
            messages.success(request, f'Asignación #{asignacion.id} marcada como COMPLETADA')
        else:
            asignacion.estado = 'CANCELADO'
            messages.warning(request, f'Asignación #{asignacion.id} CANCELADA')
        
        asignacion.observaciones = request.POST.get('observaciones', '')
        asignacion.completado_en = timezone.now()
        asignacion.save()
        return redirect('solicitudes:mis_asignaciones')
    
    return render(request, 'solicitudes/completar_asignacion.html', {'asignacion': asignacion})


def ajax_materias_por_carrera(request, carrera_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autorizado'}, status=401)
    
    try:
        carrera = Carrera.objects.get(id=carrera_id)
        docente_materias = DocenteMateria.objects.filter(
            docente=request.user,
            carrera=carrera
        ).select_related('materia')
        
        materias = [{'id': dm.materia.id, 'nombre': dm.materia.nombre} for dm in docente_materias]
        return JsonResponse({'materias': materias})
    except Carrera.DoesNotExist:
        return JsonResponse({'error': 'Carrera no encontrada'}, status=404)


def ajax_cursos_por_materia(request, materia_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autorizado'}, status=401)
    
    try:
        materia = Materia.objects.get(id=materia_id)
        docente_materias = DocenteMateria.objects.filter(
            docente=request.user,
            materia=materia
        ).select_related('curso')
        
        cursos = []
        for dm in docente_materias:
            if dm.curso:
                cursos.append({'id': dm.curso.id, 'nombre': dm.curso.nombre})
        
        if not cursos:
            cursos = [{'id': c.id, 'nombre': c.nombre} for c in materia.cursos.all()]
        
        return JsonResponse({'cursos': cursos})
    except Materia.DoesNotExist:
        return JsonResponse({'error': 'Materia no encontrada'}, status=404)


@login_required
def crear_solicitud_especial(request):
    if request.user.rol != 'DOCENTE':
        messages.error(request, 'No tienes permiso para crear solicitudes especiales')
        return redirect('solicitudes:home')

    docente = request.user

    if request.method == 'POST':
        form = SolicitudEspecialForm(request.POST, docente=docente)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.docente = docente
            solicitud.save()
            messages.success(request, f'Solicitud Especial #{solicitud.id} creada exitosamente')
            return redirect('solicitudes:mis_solicitudes_especiales')
        else:
            error_list = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label or field
                    error_list.append(f"{field_label}: {error}")
            messages.error(request, f"Errores en el formulario: {'; '.join(error_list)}")
    else:
        form = SolicitudEspecialForm(docente=docente)

    carreras_docente = docente.docente_carreras.select_related('carrera').all()

    return render(request, 'solicitudes/crear_solicitud_especial.html', {
        'form': form,
        'carreras_docente': carreras_docente
    })


@login_required
def mis_solicitudes_especiales(request):
    if request.user.rol != 'DOCENTE':
        messages.error(request, 'No tienes permiso para ver esta página')
        return redirect('solicitudes:home')

    solicitudes = request.user.solicitudes_especiales.all()
    return render(request, 'solicitudes/mis_solicitudes_especiales.html', {
        'solicitudes': solicitudes
    })


@login_required
def lista_solicitudes_especiales(request):
    if request.user.rol != 'ADMIN':
        messages.error(request, 'No tienes permiso para ver esta página')
        return redirect('solicitudes:home')

    solicitudes = SolicitudEspecial.objects.select_related('docente', 'carrera', 'materia', 'curso').all()
    estado_filter = request.GET.get('estado')
    if estado_filter:
        solicitudes = solicitudes.filter(estado=estado_filter)

    return render(request, 'solicitudes/lista_solicitudes_especiales.html', {
        'solicitudes': solicitudes,
        'estado_actual': estado_filter
    })


@login_required
def detalle_solicitud_especial(request, solicitud_id):
    solicitud = get_object_or_404(
        SolicitudEspecial.objects.select_related('docente', 'carrera', 'materia', 'curso'),
        id=solicitud_id
    )

    if request.user.rol == 'DOCENTE' and solicitud.docente != request.user:
        messages.error(request, 'No tienes permiso para ver esta solicitud')
        return redirect('solicitudes:mis_solicitudes_especiales')

    return render(request, 'solicitudes/detalle_solicitud_especial.html', {
        'solicitud': solicitud
    })


@login_required
def aprobar_solicitud_especial(request, solicitud_id):
    if request.user.rol != 'ADMIN':
        messages.error(request, 'No tienes permiso')
        return redirect('solicitudes:home')

    solicitud = get_object_or_404(SolicitudEspecial, id=solicitud_id)
    if solicitud.estado != 'PENDIENTE':
        messages.error(request, 'Esta solicitud ya fue procesada')
    else:
        solicitud.estado = 'APROBADA'
        solicitud.save()
        messages.success(request, f'Solicitud Especial #{solicitud.id} aprobada')
    return redirect('solicitudes:detalle_solicitud_especial', solicitud_id=solicitud_id)


@login_required
def rechazar_solicitud_especial(request, solicitud_id):
    if request.user.rol != 'ADMIN':
        messages.error(request, 'No tienes permiso')
        return redirect('solicitudes:home')

    solicitud = get_object_or_404(SolicitudEspecial, id=solicitud_id)

    if request.method == 'POST':
        if solicitud.estado != 'PENDIENTE':
            messages.error(request, 'Esta solicitud ya fue procesada')
            return redirect('solicitudes:detalle_solicitud_especial', solicitud_id=solicitud_id)
        solicitud.estado = 'RECHAZADA'
        solicitud.observaciones = request.POST.get('observaciones', '')
        solicitud.save()
        messages.success(request, f'Solicitud Especial #{solicitud.id} rechazada')
        return redirect('solicitudes:lista_solicitudes_especiales')

    return render(request, 'solicitudes/rechazar_solicitud_especial.html', {'solicitud': solicitud})