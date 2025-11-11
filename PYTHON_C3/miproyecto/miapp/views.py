from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, Recurso, CategoriaRecurso, FormularioContacto
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