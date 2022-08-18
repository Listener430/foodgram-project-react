# praktikum_new_diplom

# Описание/Автор
Калмыкова Надежда
Дипломный проект


# Установка на сервере
Подготовьте ВМ:
sudo apt update

sudo apt upgrade -y

sudo apt install python3-pip python3-venv git -y

sudo apt install docker.io 

sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose

sudo chown $USER /var/run/docker.sock

Скопируйте файлы:
scp nginx.conf listener@84.252.142.151:/home/listener/nginx.conf 

scp docker-compose.yml listener@84.252.142.151:/home/listener/docker-compose.yml

Запустите воркфлоу

На сервере выполните команды:
sudo docker-compose exec backend python manage.py collectstatic --no-input

sudo docker-compose exec backend python manage.py makemigrations --noinput

sudo docker-compose exec backend python manage.py migrate --noinput

sudo docker-compose exec backend python manage.py createsuperuser

sudo docker-compose exec backend python manage.py loadfile --path "./data/ingredients.csv" --model_name "Ingredient" --app_name "foodgram"

sudo docker-compose exec backend python manage.py loadfile_copy --path "./data/tags.csv" --model_name "Tag" --app_name "foodgram"

Адрес сайта:
http://84.252.142.151/recipes

суперюзер:
super@mail.ru

пароль:
super
