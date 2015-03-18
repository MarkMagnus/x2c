install requirements
$sudo apt-get install python-xlrd
$sudo pip install -r requirements.txt

django run application
$python manage.py migrate
$python manage.py runserver

django create application
$python manage.py startapp convert
$python manage.py makemigrations convert
$python manage.py migrate

create admin user
$python manage.py createsuperuser
username: root
password: elvis

play with the application
$python manage.py shell
