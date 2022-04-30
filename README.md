# efood_test

## How to run the application using django local server

1) Install basic modules for the project to run.
`pip install -r requirements.txt`

2) Prepare and Apply migrations, for the built-in user model.
You should think of migrations as a version control system for your database schema. 
makemigrations is responsible for packaging up your model changes into individual migration files - analogous to commits
migrate is responsible for applying those to your database.
`python manage.py makemigrations`

The following command applies the migrations by default to sqlite3 (usually sqlite3 is the default database in settings.py).
`python manage.py migrate`

3) Start the web application (development mode):
`python manage.py runserver` # default port 8000

4) Input files:
- datasets.csv/bq-results.csv: The full exported dataset directly from the orders table in BigQuery.
- datasets.csv/top_10_customers_orders.csv: A small list of customers that have performed the most orders from January-March 2022. Exported from BiqQuery using:

```
Identify the top 10 customer ids:

SELECT customer_id, sum(total_order_value)
FROM product-analytics-test.ds.orders
where visitor_type = 'Returning Visitor' 
group by customer_id
order by sum(total_order_value) desc
limit 10
```

```
Export the selected customer:

SELECT created_at, customer_id, order_id, total_order_value 
FROM `product-analytics-test.ds.orders`
where customer_id in (149375881,388664027,422378875,527242121,551715615,644315164,662229028,706537722,839511663,891671091)
```



4) Basic API calls supported via your browser

- To view a plot of the count(orders), sum(earnings) per day click:  http://localhost:8000/api/exploration/data_viewer/

- To view a plot of the LSTM training/testing phase for orders click: http://localhost:8000/api/exploration/data_trainer_orders/
- To view a plot of the LSTM future prediction phase for orders click: http://localhost:8000/api/exploration/data_predict_orders/

- To view a plot of the LSTM training/testing phase for earnings click: http://localhost:8000/api/exploration/data_trainer_earnings/
- To view a plot of the LSTM future prediction phase for earnings click: http://localhost:8000/api/exploration/data_predict_earnings/

5) To view the results of the MAPE scores go to logs folder

