from django.urls import path
from . import views

app_name = 'miapp'

urlpatterns = [
    # ==================== AUTENTICACIÓN ====================
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # ==================== PÁGINAS PÚBLICAS ====================
    path('', views.index, name='index'),  # Esta es tu página principal
    
    # ==================== PÁGINAS PARA USUARIOS AUTENTICADOS ====================
    path('datos-curiosos/', views.datos_curiosos, name='datos_curiosos'),
    path('recursos/', views.recursos, name='recursos'),
    path('recursos-multimedia/', views.recursos_multimedia, name='recursos_multimedia'),
    path('tests/', views.tests_psicologicos, name='tests'),
    path('contacto/', views.formulario_contacto, name='formulario_contacto'),
    
    # ==================== DASHBOARDS ESPECÍFICOS ====================
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('pasante/dashboard/', views.pasante_dashboard, name='pasante_dashboard'),
    
    # ==================== ADMINISTRACIÓN (SOLO ADMIN) ====================
    path('admin/usuarios/', views.admin_gestion_usuarios, name='admin_gestion_usuarios'),
    path('admin/recursos/', views.admin_gestion_recursos, name='admin_gestion_recursos'),
    path('admin/consultas/', views.admin_consultas, name='admin_consultas'),
    
    # ==================== PASANTE (SOLO PASANTE) ====================
    path('pasante/recursos/', views.pasante_gestion_recursos, name='pasante_gestion_recursos'),
    path('pasante/consultas/', views.pasante_consultas, name='pasante_consultas'),
]