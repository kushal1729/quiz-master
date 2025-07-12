from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()  # 👈 This creates all tables if they don't exist

if __name__ == '__main__':
    app.run()
