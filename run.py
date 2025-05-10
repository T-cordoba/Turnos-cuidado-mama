from app import create_app

app = create_app()
app.secret_key = 'b9f3e8a1c4d7e6f2a5b8c3d1f4e7a9b6'

if __name__ == '__main__':
    app.run(debug=True)