from app import db, create_app
from app.models import User, Subject, Chapter, Quiz, Question, Score

app = create_app()
with app.app_context():
    db.create_all()
    print("✅ All tables created.")    
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
