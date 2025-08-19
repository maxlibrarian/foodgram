<!-- Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API. -->

# Foodgram — «Продуктовый помощник»

**Поделись рецептом — получи список покупок. Никаких лишних слов.**

![Django](https://img.shields.io/badge/Django-4.2.16-%2315202B?logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10-%2315202B?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-%2315202B?logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-%2315202B?logo=nginx&logoColor=white)
![React](https://img.shields.io/badge/React-17.0.1-%2315202B?logo=react&logoColor=white)

**Foodgram** — это онлайн-сервис, где пользователи делятся своими любимыми рецептами, добавляют блюда в избранное, подписываются на авторов и формируют **единый список покупок** с автоматическим суммированием ингредиентов.

---

## О проекте

Foodgram — это **полноценный REST API** на Django и DRF, интегрированный с React-фронтендом и развёрнутый в Docker-контейнерах.

### Функционал:
- Публикация и просмотр рецептов
- Добавление рецептов в **список покупок**
- Скачивание **сводного списка ингредиентов**
- Добавление в **избранное**
- Подписка на авторов
- Фильтрация по тегам (`завтрак`, `обед`, `ужин`)
- Выбор ингредиентов из справочника с указанием количества
- Авторизация через **email** (Djoser)
- Режим чтения для неавторизованных

---

## Технологии

| Технология             | Версия         |
|------------------------|----------------|
| Python                 | 3.10           |
| Django                 | 4.2.16         |
| Django REST Framework  | 3.14.0         |
| Djoser                 | 2.2.0          |
| django-filter          | 23.2           |
| Pillow                 | 9.5.0          |
| psycopg2-binary        | 2.9.9          |
| gunicorn               | 20.1.0         |
| PostgreSQL             | 13.0-alpine    |
| Nginx                  | 1.19.3         |
| React                  | 17.0.1         |
| Docker                 | 20.10+         |

---

## Контейнеризация

Проект развёртывается через `docker-compose`:

```yaml
services:
  backend:
    image: mroom/foodgram_backend:latest
    build: ./backend
    command: gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
    env_file: .env
    volumes:
      - static:/var/www/foodgram/static
      - media:/app/media

  frontend:
    image: mroom/foodgram_frontend:latest
    build: ./frontend
    command: cp -r /app/build/. /static/

  gateway:
    image: mroom/foodgram_gateway:latest
    build: ./nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static:/var/www/foodgram/static
      - media:/media
      - /etc/letsencrypt:/etc/letsencrypt
      - /var/www/certbot:/var/www/certbot

  db:
    image: postgres:13.0-alpine
    env_file: .env
    volumes:
      - pg_data:/var/lib/postgresql/data

volumes:
  static:
  media:
  pg_data: