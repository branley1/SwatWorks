from app import create_app
import logging

app = create_app()

if __name__ == '__main__':
    print("Starting SwatWorks server...")
    app.run(debug=True) 