from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import (
    UserProfile, Recurso, CategoriaRecurso, FormularioContacto,
    # AGREGAR ESTAS IMPORTACIONES DEL FORO:
    CategoriaForo, HiloForo, RespuestaForo, VotoHilo, VotoRespuesta
)
from .forms import RecursoForm, UserForm, UserProfileForm


def custom_login(request):
    if request.user.is_authenticated:
        return redirigir_segun_tipo_usuario(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirigir_segun_tipo_usuario(user)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'miapp/login.html')

def redirigir_segun_tipo_usuario(user):
    try:
        if hasattr(user, 'userprofile'):
            if user.userprofile.tipo_usuario == 'admin':
                return redirect('miapp:admin_dashboard')
            elif user.userprofile.tipo_usuario == 'pasante':
                return redirect('miapp:pasante_dashboard')
        return redirect('miapp:index')
    except UserProfile.DoesNotExist:
        return redirect('miapp:index')

def custom_logout(request):
    logout(request)
    return redirect('miapp:login')

def index(request):
    return render(request, 'miapp/index.html')

@login_required
def datos_curiosos(request):
    return render(request, 'miapp/datos_curiosos.html')

@login_required
def recursos(request):
    recursos_list = Recurso.objects.filter(es_publico=True)
    return render(request, 'miapp/recursos.html', {'recursos': recursos_list})

@login_required
def recursos_multimedia(request):
    recursos_list = Recurso.objects.filter(es_publico=True)
    return render(request, 'miapp/recursos_multimedia.html', {'recursos': recursos_list})

@login_required
def tests_psicologicos(request):
    return render(request, 'miapp/tests.html')

@login_required
def formulario_contacto(request):
    if request.method == 'POST':
        tipo_consulta = request.POST.get('tipo_consulta')
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        
        FormularioContacto.objects.create(
            usuario=request.user,
            tipo_consulta=tipo_consulta,
            asunto=asunto,
            mensaje=mensaje
        )
        messages.success(request, 'Tu consulta ha sido enviada correctamente.')
        return redirect('miapp:index')
    
    return render(request, 'miapp/formulario_contacto.html')

# ==================== DASHBOARDS ====================

@login_required
def admin_dashboard(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.es_admin():
        messages.error(request, 'No tienes permisos para acceder al dashboard de administrador')
        return redirect('miapp:index')
    
    context = {
        'user': request.user,
        'stats': {
            'total_usuarios': User.objects.count(),
            'total_recursos': Recurso.objects.count(),
            'total_consultas': FormularioContacto.objects.count(),
            'consultas_sin_responder': FormularioContacto.objects.filter(respondido=False).count(),
        }
    }
    return render(request, 'miapp/admin/dashboard.html', context)

@login_required
def pasante_dashboard(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.es_pasante():
        messages.error(request, 'No tienes permisos para acceder al dashboard de pasante')
        return redirect('miapp:index')
    
    context = {
        'user': request.user,
        'stats': {
            'total_recursos': Recurso.objects.count(),
            'total_consultas': FormularioContacto.objects.count(),
            'consultas_sin_responder': FormularioContacto.objects.filter(respondido=False).count(),
        }
    }
    return render(request, 'miapp/pasante/dashboard.html', context)

# ==================== ADMINISTRACIÓN ====================

@login_required
def admin_gestion_usuarios(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.es_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('miapp:index')
    
    usuarios = User.objects.all().select_related('userprofile')
    
    if request.method == 'POST':
        if 'crear_usuario' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            tipo_usuario = request.POST.get('tipo_usuario')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya existe')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email
                )
                user.userprofile.tipo_usuario = tipo_usuario
                user.userprofile.save()
                messages.success(request, f'Usuario {username} creado exitosamente')
                
        elif 'editar_usuario' in request.POST:
            user_id = request.POST.get('user_id')
            tipo_usuario = request.POST.get('tipo_usuario')
            is_active = request.POST.get('is_active') == 'on'
            
            user = get_object_or_404(User, id=user_id)
            user.userprofile.tipo_usuario = tipo_usuario
            user.userprofile.save()
            user.is_active = is_active
            user.save()
            messages.success(request, f'Usuario {user.username} actualizado')
    
    return render(request, 'miapp/admin/gestion_usuarios.html', {'usuarios': usuarios})

@login_required
def admin_gestion_recursos(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.es_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('miapp:index')
    
    recursos_list = Recurso.objects.all().select_related('categoria', 'creado_por')
    categorias = CategoriaRecurso.objects.all()
    
    if request.method == 'POST':
        if 'crear_recurso' in request.POST:
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion')
            tipo_recurso = request.POST.get('tipo_recurso')
            categoria_id = request.POST.get('categoria')
            contenido = request.POST.get('contenido')
            es_publico = request.POST.get('es_publico') == 'on'
            
            recurso = Recurso.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                tipo_recurso=tipo_recurso,
                categoria_id=categoria_id,
                contenido=contenido,
                es_publico=es_publico,
                creado_por=request.user
            )
            messages.success(request, f'Recurso "{titulo}" creado exitosamente')
            
        elif 'editar_recurso' in request.POST:
            recurso_id = request.POST.get('recurso_id')
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion')
            tipo_recurso = request.POST.get('tipo_recurso')
            categoria_id = request.POST.get('categoria')
            contenido = request.POST.get('contenido')
            es_publico = request.POST.get('es_publico') == 'on'
            
            recurso = get_object_or_404(Recurso, id=recurso_id)
            recurso.titulo = titulo
            recurso.descripcion = descripcion
            recurso.tipo_recurso = tipo_recurso
            recurso.categoria_id = categoria_id
            recurso.contenido = contenido
            recurso.es_publico = es_publico
            recurso.save()
            messages.success(request, f'Recurso "{titulo}" actualizado')
            
        elif 'eliminar_recurso' in request.POST:
            recurso_id = request.POST.get('recurso_id')
            recurso = get_object_or_404(Recurso, id=recurso_id)
            titulo = recurso.titulo
            recurso.delete()
            messages.success(request, f'Recurso "{titulo}" eliminado')
    
    return render(request, 'miapp/admin/gestion_recursos.html', {
        'recursos': recursos_list,
        'categorias': categorias
    })

@login_required
def admin_consultas(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.es_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('miapp:index')
    
    consultas = FormularioContacto.objects.all().select_related('usuario')
    
    if request.method == 'POST':
        consulta_id = request.POST.get('consulta_id')
        respuesta = request.POST.get('respuesta')
        
        consulta = get_object_or_404(FormularioContacto, id=consulta_id)
        consulta.respuesta = respuesta
        consulta.respondido = True
        consulta.save()
        messages.success(request, 'Respuesta enviada exitosamente')
    
    return render(request, 'miapp/admin/consultas.html', {'consultas': consultas})

# ==================== PASANTE ====================

@login_required
def pasante_gestion_recursos(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.es_pasante():
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('miapp:index')
    
    recursos_list = Recurso.objects.all().select_related('categoria', 'creado_por')
    categorias = CategoriaRecurso.objects.all()
    
    if request.method == 'POST':
        if 'crear_recurso' in request.POST:
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion')
            tipo_recurso = request.POST.get('tipo_recurso')
            categoria_id = request.POST.get('categoria')
            contenido = request.POST.get('contenido')
            es_publico = request.POST.get('es_publico') == 'on'
            
            recurso = Recurso.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                tipo_recurso=tipo_recurso,
                categoria_id=categoria_id,
                contenido=contenido,
                es_publico=es_publico,
                creado_por=request.user
            )
            messages.success(request, f'Recurso "{titulo}" creado exitosamente')
            
        elif 'editar_recurso' in request.POST:
            recurso_id = request.POST.get('recurso_id')
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion')
            tipo_recurso = request.POST.get('tipo_recurso')
            categoria_id = request.POST.get('categoria')
            contenido = request.POST.get('contenido')
            es_publico = request.POST.get('es_publico') == 'on'
            
            recurso = get_object_or_404(Recurso, id=recurso_id, creado_por=request.user)
            recurso.titulo = titulo
            recurso.descripcion = descripcion
            recurso.tipo_recurso = tipo_recurso
            recurso.categoria_id = categoria_id
            recurso.contenido = contenido
            recurso.es_publico = es_publico
            recurso.save()
            messages.success(request, f'Recurso "{titulo}" actualizado')
            
        elif 'eliminar_recurso' in request.POST:
            recurso_id = request.POST.get('recurso_id')
            recurso = get_object_or_404(Recurso, id=recurso_id, creado_por=request.user)
            titulo = recurso.titulo
            recurso.delete()
            messages.success(request, f'Recurso "{titulo}" eliminado')
    
    return render(request, 'miapp/pasante/gestion_recursos.html', {
        'recursos': recursos_list,
        'categorias': categorias
    })

@login_required
def pasante_consultas(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.es_pasante():
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('miapp:index')
    
    consultas = FormularioContacto.objects.all().select_related('usuario')
    
    if request.method == 'POST':
        consulta_id = request.POST.get('consulta_id')
        respuesta = request.POST.get('respuesta')
        
        consulta = get_object_or_404(FormularioContacto, id=consulta_id)
        consulta.respuesta = respuesta
        consulta.respondido = True
        consulta.save()
        messages.success(request, 'Respuesta enviada exitosamente')
    
    return render(request, 'miapp/pasante/consultas.html', {'consultas': consultas})

# ==================== VISTAS FORO COMUNITARIO ====================# ==================== VISTAS FORO COMUNITARIO ====================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import (
    UserProfile, Recurso, CategoriaRecurso, FormularioContacto,
    # AGREGAR ESTAS IMPORTACIONES DEL FORO:
    CategoriaForo, HiloForo, RespuestaForo
)
from .forms import RecursoForm, UserForm, UserProfileForm

# ... (tus vistas existentes aquí)

# ==================== VISTAS FORO COMUNITARIO SIMPLIFICADAS ==
@login_required
def foro_comunitario(request):
    """Vista principal del foro comunitario"""
    # Crear categorías por defecto si no existen
    if not CategoriaForo.objects.exists():
        categorias_default = [
            {'nombre': 'Experiencias Personales', 'color': '#6C63FF', 'orden': 1},
            {'nombre': 'Consejos y Estrategias', 'color': '#4CAF50', 'orden': 2},
            {'nombre': 'Apoyo Emocional', 'color': '#FF6B6B', 'orden': 3},
            {'nombre': 'Preguntas y Dudas', 'color': '#FFA726', 'orden': 4},
        ]
        for cat_data in categorias_default:
            CategoriaForo.objects.create(
                nombre=cat_data['nombre'],
                color=cat_data['color'],
                orden=cat_data['orden']
            )
    
    categorias = CategoriaForo.objects.filter(es_activa=True).order_by('orden')
    
    # Filtros - solo se aplican cuando se presiona el botón
    categoria_id = request.GET.get('categoria', '')
    orden = request.GET.get('orden', 'recientes')
    
    # Query base
    hilos = HiloForo.objects.select_related('categoria', 'creado_por', 'creado_por__userprofile')
    
    # Aplicar filtros solo si se envió el formulario
    if 'aplicar_filtros' in request.GET:
        if categoria_id and categoria_id != 'todas':
            hilos = hilos.filter(categoria_id=categoria_id)
    
    # Aplicar ordenamiento CORREGIDO
    if orden == 'populares':
        hilos = hilos.order_by('-votos_positivos', '-visitas', '-actualizado_en')
    elif orden == 'antiguos':
        hilos = hilos.order_by('creado_en')
    else:  # recientes (POR DEFECTO)
        hilos = hilos.order_by('-creado_en')  # Cambiado de -actualizado_en a -creado_en
    
    # Estadísticas
    stats = {
        'total_hilos': HiloForo.objects.count(),
        'total_respuestas': RespuestaForo.objects.count(),
        'hilos_abiertos': HiloForo.objects.filter(estado='abierto').count(),
    }
    
    context = {
        'hilos': hilos,
        'categorias': categorias,
        'categoria_actual': categoria_id,
        'orden_actual': orden,
        'stats': stats,
    }
    
    return render(request, 'miapp/foro_comunitario.html', context)

@login_required
def crear_hilo(request):
    """Vista para crear un nuevo hilo"""
    categorias = CategoriaForo.objects.filter(es_activa=True).order_by('orden')
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        categoria_id = request.POST.get('categoria')
        es_anonimo = request.POST.get('es_anonimo') == 'on'
        
        if titulo and contenido and categoria_id:
            hilo = HiloForo.objects.create(
                titulo=titulo,
                contenido=contenido,
                categoria_id=categoria_id,
                creado_por=request.user,
                es_anonimo=es_anonimo
            )
            messages.success(request, 'Tu hilo ha sido creado exitosamente.')
            return redirect('miapp:detalle_hilo', hilo_id=hilo.id)
        else:
            messages.error(request, 'Por favor completa todos los campos obligatorios.')
    
    context = {
        'categorias': categorias,
    }
    
    return render(request, 'miapp/crear_hilo.html', context)

@login_required
def editar_hilo(request, hilo_id):
    """Vista para editar un hilo existente"""
    hilo = get_object_or_404(HiloForo, id=hilo_id)
    
    # Solo el creador puede editar el hilo
    if request.user != hilo.creado_por:
        messages.error(request, 'No tienes permisos para editar este hilo.')
        return redirect('miapp:detalle_hilo', hilo_id=hilo_id)
    
    categorias = CategoriaForo.objects.filter(es_activa=True).order_by('orden')
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        categoria_id = request.POST.get('categoria')
        es_anonimo = request.POST.get('es_anonimo') == 'on'
        
        if titulo and contenido and categoria_id:
            hilo.titulo = titulo
            hilo.contenido = contenido
            hilo.categoria_id = categoria_id
            hilo.es_anonimo = es_anonimo
            hilo.save()
            
            messages.success(request, 'Tu hilo ha sido actualizado exitosamente.')
            return redirect('miapp:detalle_hilo', hilo_id=hilo.id)
        else:
            messages.error(request, 'Por favor completa todos los campos obligatorios.')
    
    context = {
        'hilo': hilo,
        'categorias': categorias,
    }
    
    return render(request, 'miapp/editar_hilo.html', context)

@login_required
def detalle_hilo(request, hilo_id):
    """Vista para ver un hilo específico y sus respuestas"""
    hilo = get_object_or_404(
        HiloForo.objects.select_related('categoria', 'creado_por', 'creado_por__userprofile'),
        id=hilo_id
    )
    
    # Incrementar contador de visitas
    hilo.visitas += 1
    hilo.save()
    
    respuestas = hilo.respuestas.select_related('creado_por', 'creado_por__userprofile').order_by('creado_en')
    
    if request.method == 'POST':
        contenido = request.POST.get('contenido_respuesta')
        es_anonimo = request.POST.get('es_anonimo') == 'on'
        
        if contenido:
            RespuestaForo.objects.create(
                hilo=hilo,
                contenido=contenido,
                creado_por=request.user,
                es_anonimo=es_anonimo
            )
            messages.success(request, 'Tu respuesta ha sido publicada exitosamente.')
            return redirect('miapp:detalle_hilo', hilo_id=hilo.id)
    
    context = {
        'hilo': hilo,
        'respuestas': respuestas,
    }
    
    return render(request, 'miapp/detalle_hilo.html', context)

@login_required
def eliminar_hilo(request, hilo_id):
    """Vista para eliminar un hilo (solo admin/pasante)"""
    hilo = get_object_or_404(HiloForo, id=hilo_id)
    
    # Verificar permisos: SOLO admin o pasante pueden eliminar
    puede_eliminar = (
        hasattr(request.user, 'userprofile') and 
        (request.user.userprofile.es_admin() or request.user.userprofile.es_pasante())
    )
    
    if not puede_eliminar:
        messages.error(request, 'No tienes permisos para eliminar hilos. Solo el staff puede eliminar hilos.')
        return redirect('miapp:detalle_hilo', hilo_id=hilo_id)
    
    if request.method == 'POST':
        titulo = hilo.titulo
        hilo.delete()
        messages.success(request, f'El hilo "{titulo}" ha sido eliminado exitosamente.')
        return redirect('miapp:foro_comunitario')
    
    context = {
        'hilo': hilo,
    }
    
    return render(request, 'miapp/eliminar_hilo.html', context)