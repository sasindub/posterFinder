Install Flask, Flask-PyMongo, and other required packages
    - pip install Flask Flask-PyMongo pytesseract pillow

Flask==2.3.3
Flask-PyMongo==3.3.1
pytesseract==0.3.10
pillow==9.5.0
    -pip install -r requirements.txt

#.env file

The .env file is used to store environment variables in a key-value pair format for your application. These variables can include configuration settings like database URLs, API keys, or any other secret information that you don't want to hard-code in your source files or expose in your version control system.

Using a .env file helps in:

Configuration Management: Easily manage different configurations for development, testing, and production environments.
Security: Keep sensitive information out of your codebase.
Convenience: Easily change configurations without modifying code.

Install python-dotenv:

To load environment variables from the .env file, use the python-dotenv package. Install it: 
    -pip install python-dotenv

