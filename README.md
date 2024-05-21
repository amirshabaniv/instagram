## Installation and run project
#### Create venv and use pip to install packages in project
```python
python pip install -r requirements.txt
```

#### Configure the postgres database in the settings.py file and mekemigration and migrate:
```python
python manage.py makemigrations
python manage.py migrate
```

#### Run project
```python
python manage.py runserver
```
