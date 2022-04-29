# efood_test

## How to run the application using django local server

1) Install basic modules for the project to run.
`pip3 install -r requirements.txt`

2) Prepare and Apply migrations, for the built-in user model.
You should think of migrations as a version control system for your database schema. 
makemigrations is responsible for packaging up your model changes into individual migration files - analogous to commits
migrate is responsible for applying those to your database.
`python3 manage.py makemigrations`

The following command applies the migrations by default to sqlite3 (usually sqlite3 is the default database in settings.py).
`python3 manage.py migrate`

3) Start the application (development mode):
`python3 manage.py runserver` # default port 8000

4) Basic API calls supported via your browser

- To view a plot of the count(orders), sum(earnings) per day click:  http://localhost:8000/api/exploration/data_viewer/

- To view a plot of the results of the LSTM testing phase for orders click: http://localhost:8000/api/exploration/data_trainer_orders/

- To view a plot of the results of the LSTM testing phase for earnings click: http://localhost:8000/api/exploration/data_trainer_earnings/

5) To view the results of the MAPE scores go to logs folder

