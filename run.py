from app import create_app, db
from app.models import User

app = create_app()

# ✅ Fix: Wrap DB logic in app context
with app.app_context():
    db.create_all()

    # Check if admin user already exists
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
        print("Admin user created successfully!")

# Run the app locally (not used on Render)
if __name__ == '__main__':
    app.run()
