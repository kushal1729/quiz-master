from app import create_app, db

app = create_app()

# Initialize DB if not exists
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
