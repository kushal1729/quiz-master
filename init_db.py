from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
app.app_context().push()

# Create DB tables
db.create_all()
print("✅ Tables created")

# Add admin if not exists
if not User.query.filter_by(username='admin').first():
    admin = User(
        username='admin',
        password=generate_password_hash('admin123'),
        full_name='Admin User',
        qualification='Admin',
        dob='2005-04-15',
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin created: admin/admin123")
else:
    print("✅ Admin already exists")
