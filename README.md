# web-programming-2026-template

A reusable Django project with no bundled application, SQLite, and Django's
standard admin, authentication, sessions, messages, and staticfiles support.

## Local setup

Requires the latest patch release of Python 3.12, 3.13, or 3.14. Run these commands from the project directory containing
`manage.py`.

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   
   # for linux/macos
   source .venv/bin/activate
   # for Windows:
   .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   python -m pip install -r requirements-dev.txt
   ```


3. Apply migrations to create the local SQLite database:

   ```bash
   python manage.py migrate
   ```

4. Start the development server:

   ```bash
   python manage.py runserver
   ```

## Endpoints

With the server running at `http://127.0.0.1:8000`:

| URL | Behavior |
| --- | --- |
| http://127.0.0.1:8000/ | No application homepage; may show Django's development welcome page while `DEBUG = True` |
| http://127.0.0.1:8000/admin/ | Django admin, available after applying migrations |

With `DEBUG = False`, unmatched URLs such as `/` return HTTP 404.

To create an account for admin login, run this after applying migrations:

```bash
python manage.py createsuperuser
```

## Add your first application

1. Create an app from the directory containing `manage.py` (replace `myapp`
   with your application name):

   ```bash
   python manage.py startapp myapp
   ```

2. Add its generated configuration class, `myapp.apps.MyappConfig`, to
   `INSTALLED_APPS` in `config/settings.py`.
3. Define your views and create `myapp/urls.py` with their URL patterns.
4. Register that URLconf in `config/urls.py` using `path()` and `include()`,
   choosing a URL prefix for the app and retaining the admin route.

See the official Django 6.1 tutorial for
[views and URL registration](https://docs.djangoproject.com/en/6.1/intro/tutorial01/)
and [app registration and models](https://docs.djangoproject.com/en/6.1/intro/tutorial02/).

## Start a REST API

Django REST framework and `django-cors-headers` are included and configured.
Install the project dependencies with `python -m pip install -r requirements-dev.txt`.
Create your own app, serializers, views, and URL patterns; no API app or
authentication scheme is supplied.

## Git attributes

Git detects text files automatically and normalizes them to LF. Checkouts use
LF on Linux and Windows, while `.bat` and `.cmd` files use CRLF. Binary files
are auto-detected and left unchanged, helping avoid newline-only diffs.


## Code style and submission verification

All submissions are required to adhere to PEP-8, Django best practices, and standard HTML/CSS/JS formatting. A deterministic cross-platform utility is provided to help you check and format your code.

### 1. Verification (Check Mode)
Before submitting, verify that all files adhere to the required standards:

```bash
python check_submission.py
```

Passing these checks confirms code style, not functional API behavior. Before submitting an API, also write and run functional tests for its endpoints. If style checks fail, review the error output or run the auto-formatter below.

### 2. Auto-Formatting
To automatically format Python files, fix safe PEP-8 rules, format Django HTML templates, and format CSS/JS static files:

```bash
python check_submission.py --format
```

### 3. PyCharm Integration
If you use PyCharm:
- **One-Click Run:** In the top-right toolbar run configurations dropdown, select **"Verify Submission"** or **"Format Project"** and click the green **Play** button.

## Development only

The included settings use `DEBUG = True`, a development secret key, and a local
SQLite database. The default mailer uses the console backend: email is printed
to the process's console instead of being delivered.

This configuration and Django's development server are not suitable for
production deployment.


# Інтернет-сервіс Eventify для купівлі електронних квитків на різноманітні концертно-розважальні та культурні події

## Команда
- Бурдейна Інна
- Матійцьо Вікторія
- Муратова Олександра

## Опис
Вебсервіс для зручного пошуку, вибору та купівлі електронних квитків на культурні й концертно-розважальні події. Платформа допомагає відвідувачам швидко знаходити цікаві заходи у своєму місті та безпечно бронювати квитки, а організаторам ефективно керувати продажами й аналітикою подій.

## Ролі
- Гість: перегляд каталогу подій, пошук та фільтрація за категоріями/містом/датою, перегляд деталей події та доступних місць, реєстрація та вхід.
- Користувач: функціонал Гостя, вибір місць на графічній схемі залу, купівля та онлайн-оплата квитків, перегляд придбаних квитків у особистому кабінеті, скачування квитків із QR-кодом, повернення квитків.
- Організатор: функціонал Користувача, створення та редагування власних подій, налаштування схем залу та цін по зонах, перегляд статистики продажів і виручки по своїх заходах.
- Адміністратор: повний доступ до системи, модерація подій організаторів, управління користувачами та блокування акаунтів, перегляд загальносистемної аналітики.

## Основний функціонал
- Каталог та пошук: фільтрація подій за категоріями (концерти, театр, фестивалі), датою, ціною та розташуванням.
- Інтерактивна схема залу: вибір конкретних місць у залі із динамічним відображенням їхнього статусу (вільно / заброньовано / продано).
- Аутентифікація та захист: безпечний вхід за допомогою JWT з розмежуванням прав доступу на основі ролей.
- Особистий кабінет: історія покупок, збережені квитки у вигляді електронних перепусток із QR-кодом.
- Адмін-панель: інструменти для підтвердження нових подій від організаторів та відстеження продажів.

## Особливість проєкту
- Вбудований чат-бот підтримки: інтегрований у вебінтерфейс віджет чат-бота для швидких відповідей на часті запитання (FAQ: як повернути квиток, де знайти придбаний квиток, способи оплати тощо).
- Автоматична розсилка та нотифікації: інтеграція з Email-сервісом для надсилання куплених квитків у форматі PDF разом із QR-кодом.
- Генерація та валідація QR-кодів: створення унікальних QR-кодів для кожного квитка з можливістю їхньої перевірки на вході.