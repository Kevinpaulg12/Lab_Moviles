"""
Script de gestión de usuarios para SISOL
Uso: python manage.py shell < scripts/usuarios.py
"""
from accounts.models import Usuario

def listar_usuarios():
    """Lista todos los usuarios en el sistema"""
    print('\n=== USUARIOS EN EL SISTEMA ===')
    print('-' * 50)
    for u in Usuario.objects.all():
        print(f'  {u.username:20} | {u.rol:12} | {u.email}')
    print('-' * 50)
    print(f'Total: {Usuario.objects.count()} usuarios\n')

def reset_passwords():
    """Reset contraseñas a password123 para usuarios de prueba"""
    from django.contrib.auth.hashers import make_password
    
    usuarios = {
        'admin': 'password123',
        'jcano': 'password123',
        'pgomez': 'password123',
        'mrodriguez': 'password123',
        'lfernandez': 'password123',
        'rgarcia': 'password123',
    }
    
    print('\n=== RESETEAR CONTRASEÑAS ===')
    for username, password in usuarios.items():
        try:
            user = Usuario.objects.get(username=username)
            user.password = make_password(password)
            user.save()
            print(f'✓ {username}: password123')
        except Usuario.DoesNotExist:
            print(f'✗ {username}: No encontrado')

def crear_usuarios_demo():
    """Crea usuarios de demostración"""
    from django.contrib.auth.hashers import make_password
    
    demo_users = [
        {'username': 'demo_admin', 'email': 'demo_admin@unemi.edu.ec', 'rol': 'ADMIN'},
        {'username': 'demo_docente', 'email': 'demo_docente@unemi.edu.ec', 'rol': 'DOCENTE'},
        {'username': 'demo_responsable', 'email': 'demo_resp@unemi.edu.ec', 'rol': 'RESPONSABLE'},
    ]
    
    print('\n=== CREAR USUARIOS DEMO ===')
    for data in demo_users:
        if not Usuario.objects.filter(username=data['username']).exists():
            user = Usuario.objects.create(
                username=data['username'],
                email=data['email'],
                rol=data['rol'],
                password=make_password('demo123')
            )
            print(f'✓ Creado: {data["username"]} (demo123)')
        else:
            print(f'- Ya existe: {data["username"]}')

# Ejecutar funciones
listar_usuarios()
# Descomenta las que necesites:
# reset_passwords()
# crear_usuarios_demo()