from app import create_app, db

app = create_app()

from app.models import User

# Check if admin exists
if not User.query.filter_by(username='admin').first():
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

if __name__ == '__main__':
    app.run()
