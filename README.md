## Installtion
#### Create venv and use pip to install packages in project
pip install -r requirements.txt

#### Configure the postgres database in the settings.py file and mekemigration:
python manage.py makemigrations
python manage.py migrate

#### Run project
python manage.py runserver