from app import db, create_app
from app.models import User
app = create_app()
    admin_user = User(
        username='admin',
        password='admin123',
        full_name='Admin User',
        qualification='Admin',
        dob='2005-04-15',
        is_admin=True  
    )
    db.session.add(admin_user)
    db.session.commit()
    print("Admin user created successfully!")
