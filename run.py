from flask import Flask
from app import db
from app.routes import main
from app.models import User
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
app.register_blueprint(main)

# ✅ Add this block
with app.app_context():
    db.create_all()

    # Ensure admin user exists
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            password=generate_password_hash('admin123'),
            full_name='Admin User',
            qualification='Admin',
            dob='2005-04-15',
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()

# This should be at the end of your app.py
if __name__ == "__main__":
    app.run(debug=True)
