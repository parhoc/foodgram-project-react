# Foodgram

## О проекте
«Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
## Доступ к сайту
Сайт: https://foodgram.viewdns.net

Email: foodgram@foodgram.com

Пароль: foodgram5533
## Установка
### Подготовка
Для запуска проекта необходим Docker и Docker compose. Если они уже установлен, то шаг подготовки можно пропустить.

Скачайть и установить curl:
```
sudo apt update
sudo apt install curl
```
С помощью утилиты curl скачать скрипт для установки докера с официального сайта:
```
curl -fSL https://get.docker.com -o get-docker.sh
```
Запустить сохранённый скрипт с правами суперпользователя:
```
sudo sh ./get-docker.sh
```
Установить утилиту Docker Compose:
```
sudo apt install docker-compose-plugin
```
### Через Docker hub
Скачать файл ``docker-compose.production.yml``

В директории с файлом запустить:
```
docker compose -f docker-compose.production.yml up -d
```
Ввести команду для настройки базы данных:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
Собрать статуку:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
#### Установка и настройка Nginx
Если Nginx уже установлен, то загрузку и запуск можно пропустить.

Установить Nginx:
```
sudo apt install nginx -y
```
Запустить Nginx командой:
```
sudo systemctl start nginx
```
Обновить настройки Nginx:
```
sudo nano /etc/nginx/sites-enabled/default
```
В открывшемся файле записать настройки сервера:
```
server {
  listen 80;
  server_name ваш_домен;

  location / {
    proxy_pass http://127.0.0.1:8000;
  }
}
```
Сохраните и закройте файл.

Перезагрузите конфигурацию Nginx:
```
sudo systemctl reload nginx
```
Сайт будет доступен по вашему домену.
### Локальная установка
Клонировать рапозиторий:
```
git clone https://github.com/parhoc/foodgram-project-react.git
```
В папке с проектом запустить Docker compose:
```
docker compose up -d
```
Ввести команду для настройки базы данных:
```
sudo docker compose exec backend python manage.py migrate
```
Собрать статуку:
```
sudo docker compose exec backend python manage.py collectstatic
sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
```
Сайт будет доступен по адресу `127.0.0.1:8000`.
## Технические характеристики
Docker compose включает три контейнера:
* frontend - NodeJS 13.12;
* backend - Python 3.10, Django 3.2 и Djangorestframework 3.14;
* db - PostgreSQL 13;
* gateway - Nginx 1.19.3.
## Возможности проекта
### Рецепты
![alt text](https://pictures.s3.yandex.net/resources/S16_01_1692340098.png)
На главной странице сайта показываются все рецепты в порядке создания. На странице рецепта можно посмотреть более детальную информацию, а авторизированные пользователи могут добавить рецепт в избранное или список покупок. Рецепты можно фильтровать по тегам и авторам.
### Добавление рецепта
![alt text](https://pictures.s3.yandex.net/resources/S16_09_1_1692340285.png)
Пользователи могут добавлять собственные рецепты. Для этого пользователю необходимо указать названи рецепта, выбрать подходещие теги, нужные ингредиетны, указать время готовки, добавить описание и картинку рецепта.
### Список покупок и избранное
![alt text](https://pictures.s3.yandex.net/resources/S16_07_1692340247.png)
Каждый рецепт можно добавить в список покупок или избранное. Список покупок можно скачать в виде PDF файла с необходимыми для рецептов ингредиентами их количеством.
