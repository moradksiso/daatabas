"""
Script para recrear la base de datos
"""
import os
from app import app, db, User

def reset_database():
    """Recrear la base de datos"""
    # Buscar la base de datos
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files.db')
    instance_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'files.db')
    
    # Eliminar la base de datos si existe
    if os.path.exists(db_path):
        print(f"Eliminando base de datos: {db_path}")
        os.remove(db_path)
    
    if os.path.exists(instance_db_path):
        print(f"Eliminando base de datos: {instance_db_path}")
        os.remove(instance_db_path)
    
    # Crear la base de datos
    with app.app_context():
        print("Creando tablas...")
        db.create_all()
        
        # Crear usuario administrador
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Creando usuario administrador...")
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Usuario administrador creado (admin/admin123)")
        
        print("Base de datos recreada con éxito")

if __name__ == "__main__":
    reset_database()
