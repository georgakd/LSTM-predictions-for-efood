# efood_test

## How to run the application using django local server

Install basic modules for the project to run.
`pip3 install -r requirements.txt`

Apply migrations, if using a user data model.
You should think of migrations as a version control system for your database schema. 
makemigrations is responsible for packaging up your model changes into individual migration files - analogous to commits 
migrate is responsible for applying those to your database.
`python3 manage.py makemigrations`

The following command applies the migrations by default to sqlite3 (usually sqlite3 is the default database in settings.py).
`python3 manage.py migrate`

Start the application (development mode):
`python3 manage.py runserver` # default port 8000

