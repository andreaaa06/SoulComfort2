from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('admin', 'Administrador'),
        ('pasante', 'Pasante de Psicología'),
        ('paciente', 'Paciente'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES, default='paciente')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_usuario_display()}"
    
    # Método para verificar fácilmente el tipo de usuario
    def es_admin(self):
        return self.tipo_usuario == 'admin'
    
    def es_pasante(self):
        return self.tipo_usuario == 'pasante'
    
    def es_paciente(self):
        return self.tipo_usuario == 'paciente'

# Señales para crear el profile automáticamente
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

# Categorías para los recursos
class CategoriaRecurso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6C63FF')
    
    def __str__(self):
        return self.nombre

# Recursos multimedia
class Recurso(models.Model):
    TIPO_RECURSO_CHOICES = [
        ('video', 'Video'),
        ('articulo', 'Artículo'),
        ('texto_imagen', 'Texto con Imágenes'),
        ('ejercicio', 'Ejercicio Práctico'),
    ]
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo_recurso = models.CharField(max_length=15, choices=TIPO_RECURSO_CHOICES)
    categoria = models.ForeignKey(CategoriaRecurso, on_delete=models.CASCADE)
    url = models.URLField(blank=True, null=True)
    archivo = models.FileField(upload_to='recursos/', blank=True, null=True)
    contenido = models.TextField(blank=True)
    es_publico = models.BooleanField(default=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.titulo

# Tests psicológicos
class TestPsicologico(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    instrucciones = models.TextField()
    es_activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

class PreguntaTest(models.Model):
    test = models.ForeignKey(TestPsicologico, on_delete=models.CASCADE, related_name='preguntas')
    texto_pregunta = models.TextField()
    orden = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
    
    def __str__(self):
        return f"Pregunta {self.orden}: {self.texto_pregunta[:50]}..."

class OpcionRespuesta(models.Model):
    pregunta = models.ForeignKey(PreguntaTest, on_delete=models.CASCADE, related_name='opciones')
    texto_opcion = models.CharField(max_length=200)
    valor = models.IntegerField()
    categoria_recomendacion = models.ForeignKey(CategoriaRecurso, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.texto_opcion

class ResultadoTest(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(TestPsicologico, on_delete=models.CASCADE)
    puntuacion_total = models.IntegerField()
    categoria_recomendada = models.ForeignKey(CategoriaRecurso, on_delete=models.CASCADE)
    completado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Resultado de {self.usuario.username} - {self.test.nombre}"

# Formulario de contacto
class FormularioContacto(models.Model):
    TIPO_CONSULTA_CHOICES = [
        ('sugerencia', 'Sugerencia'),
        ('duda', 'Duda'),
        ('problema', 'Problema Técnico'),
        ('otros', 'Otros'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_consulta = models.CharField(max_length=20, choices=TIPO_CONSULTA_CHOICES)
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    respondido = models.BooleanField(default=False)
    respuesta = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.asunto} - {self.usuario.username}"
    
# ==================== MODELOS FORO COMUNITARIO ====================
# ==================== MODELOS FORO COMUNITARIO ====================

class CategoriaForo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6C63FF')
    orden = models.IntegerField(default=0)
    es_activa = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Categoría del Foro'
        verbose_name_plural = 'Categorías del Foro'
    
    def __str__(self):
        return self.nombre

class HiloForo(models.Model):
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'),
        ('cerrado', 'Cerrado'),
        ('destacado', 'Destacado'),
    ]
    
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    categoria = models.ForeignKey(CategoriaForo, on_delete=models.CASCADE)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hilos_creados')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='abierto')
    es_anonimo = models.BooleanField(default=False)
    votos_positivos = models.IntegerField(default=0)
    votos_negativos = models.IntegerField(default=0)
    visitas = models.IntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-actualizado_en']
        verbose_name = 'Hilo del Foro'
        verbose_name_plural = 'Hilos del Foro'
    
    def __str__(self):
        return self.titulo
    
    def total_respuestas(self):
        return self.respuestas.count()
    
    def ultima_respuesta(self):
        return self.respuestas.order_by('-creado_en').first()

class RespuestaForo(models.Model):
    hilo = models.ForeignKey(HiloForo, on_delete=models.CASCADE, related_name='respuestas')
    contenido = models.TextField()
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='respuestas_foro')
    es_anonimo = models.BooleanField(default=False)
    es_respuesta_oficial = models.BooleanField(default=False)
    votos_positivos = models.IntegerField(default=0)
    votos_negativos = models.IntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['creado_en']
        verbose_name = 'Respuesta del Foro'
        verbose_name_plural = 'Respuestas del Foro'
    
    def __str__(self):
        return f"Respuesta a: {self.hilo.titulo}"

class VotoHilo(models.Model):
    TIPO_VOTO_CHOICES = [
        ('positivo', 'Positivo'),
        ('negativo', 'Negativo'),
    ]
    
    hilo = models.ForeignKey(HiloForo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_voto = models.CharField(max_length=10, choices=TIPO_VOTO_CHOICES)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['hilo', 'usuario']
        verbose_name = 'Voto de Hilo'
        verbose_name_plural = 'Votos de Hilos'

class VotoRespuesta(models.Model):
    TIPO_VOTO_CHOICES = [
        ('positivo', 'Positivo'),
        ('negativo', 'Negativo'),
    ]
    
    respuesta = models.ForeignKey(RespuestaForo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_voto = models.CharField(max_length=10, choices=TIPO_VOTO_CHOICES)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['respuesta', 'usuario']
        verbose_name = 'Voto de Respuesta'
        verbose_name_plural = 'Votos de Respuestas'