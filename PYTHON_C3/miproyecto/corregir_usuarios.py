import os
import django
import sys

# Agregar el directorio del proyecto al path de Python
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miproyecto.settings')
django.setup()

from django.contrib.auth.models import User
from miapp.models import UserProfile

def corregir_usuarios():
    print("🔧 Iniciando corrección de usuarios...")
    
    # Diccionario con usuarios y sus tipos correctos
    usuarios = {
        'admin_soul': 'admin',
        'pasante_ana': 'pasante', 
        'paciente_carlos': 'paciente',
        'admin': 'admin'  # Por si acaso el superusuario también necesita corrección
    }
    
    usuarios_corregidos = 0
    usuarios_no_encontrados = []
    
    for username, tipo in usuarios.items():
        try:
            user = User.objects.get(username=username)
            
            # Obtener o crear el perfil de usuario
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Verificar si el tipo necesita actualización
            if profile.tipo_usuario != tipo:
                profile.tipo_usuario = tipo
                profile.save()
                print(f"✅ {username} actualizado de '{profile.tipo_usuario}' a '{tipo}'")
                usuarios_corregidos += 1
            else:
                print(f"ℹ️  {username} ya tiene el tipo correcto: {tipo}")
                
        except User.DoesNotExist:
            print(f"❌ Usuario {username} no encontrado")
            usuarios_no_encontrados.append(username)
    
    print(f"\n📊 RESUMEN:")
    print(f"Usuarios corregidos: {usuarios_corregidos}")
    print(f"Usuarios no encontrados: {len(usuarios_no_encontrados)}")
    
    if usuarios_no_encontrados:
        print(f"Usuarios faltantes: {', '.join(usuarios_no_encontrados)}")
    
    # Mostrar estado actual de todos los usuarios
    print(f"\n👥 ESTADO ACTUAL DE USUARIOS:")
    todos_usuarios = User.objects.all()
    for user in todos_usuarios:
        try:
            profile = user.userprofile
            print(f"   {user.username} - {profile.get_tipo_usuario_display()} ({profile.tipo_usuario})")
        except UserProfile.DoesNotExist:
            print(f"   {user.username} - SIN PERFIL (creando...)")
            UserProfile.objects.create(user=user, tipo_usuario='paciente')
            print(f"   {user.username} - Perfil creado como 'paciente'")

if __name__ == "__main__":
    corregir_usuarios()
    print("\n🎯 ¡Corrección completada!")