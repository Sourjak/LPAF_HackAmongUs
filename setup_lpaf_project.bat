@echo off

echo Creating LPAF Project Structure...

cd /d "C:\Users\sourj\OneDrive\Desktop"

mkdir LPAF_CS
cd LPAF_CS

echo Creating core files...
type nul > app.py
type nul > requirements.txt
type nul > README.md
type nul > Procfile

echo Creating template folders...
mkdir templates
type nul > templates\index.html
type nul > templates\professor.html
type nul > templates\student.html
type nul > templates\success.html

echo Creating static folders...
mkdir static
mkdir static\css
mkdir static\js
mkdir static\assets
mkdir static\assets\icons
mkdir static\assets\images

type nul > static\css\styles.css
type nul > static\js\qr.js
type nul > static\js\validation.js

echo Creating database folder...
mkdir database
type nul > database\attendance.db

echo Creating utility modules...
mkdir utils
type nul > utils\token_manager.py
type nul > utils\qr_generator.py
type nul > utils\validator.py

echo Project structure created successfully.

pause