install requirements
$sudo pip install -r requirements.txt
$sudo apt-get install python-xlrd

django application
create project
$python manage.py migrate
$python manage.py runserver

create application
$python manage.py startapp convert
$python manage.py makemigrations convert
$python manage.py migrate

create admin user
$python manage.py createsuperuser
username: root
password: elvis

play with the application
$python manage.py shell
