# 📞 HotLine Project

Добро пожаловать в проект **HotLine**! Это веб-приложение, предназначенное для управления вопросами и ответами, с возможностью поиска и аналитики.

## 📋 Содержание
- [Описание](#описание)
- [Технологии](#технологии)
- [Установка](#установка)
- [Настройка](#настройка)
- [Запуск](#запуск)
- [Использование](#использование)
- [Отладка](#отладка)

## 📝Описание

**HotLine** — это FastAPI приложение, которое позволяет:
- Управлять категориями и подкатегориями вопросов.
- Выполнять поиск вопросов с поддержкой fuzzy-поиска.
- Анализировать вопросы и их корреляцию.
- Отправлять уведомления и письма через интеграцию с FastMail.

## 💻Технологии

Проект построен с использованием следующих технологий:
- **Python** (версия 3.12+)
- **FastAPI** — асинхронный веб-фреймворк.
- **PostgreSQL** — реляционная база данных.
- **Alembic** — инструмент для управления миграциями.
- **Asyncpg** — асинхронный драйвер для PostgreSQL.
- **Uvicorn** — ASGI-сервер для запуска приложения.
- **Pydantic** — для валидации данных.

## 🚀Установка
### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/hotline.git
cd hotline
```


### 2. Создание и активация виртуального окружения
На Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

На Linux и macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r req.txt
```

## ⚙️Настройка
### 1. Настройка переменных окружения
Создайте файл .env в корне проекта и добавьте следующие переменные:
```bash
env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/db_name
SECRET_KEY=ваш_секретный_ключ
SMTP_USER=ваш_email@домен.com
SMTP_PASSWORD=ваш_пароль
TIMEZONE="Europe/Yekaterinburg"
```

### 2. Создание баз данных по миграциям
```bash
alembic revision --autogenerate -m "nitial revision"
```

### 3. Применение миграций
```bash
alembic upgrade head
```

## ▶️Запуск
### 1. Локальный сервер
Для запуска приложения выполните команду:

```bash
uvicorn app.main:app --reload
```

#### Приложение будет доступно по адресу: http://localhost:8000

## 2. Запуск в режиме production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 80
```

## 📚Использование
```bash
Документация доступна по адресу: http://localhost:8000/docs
Также доступен интерфейс Redoc: http://localhost:8000/redoc
```

## 🐛Отладка

Если возникают ошибки при запуске, проверьте лог-файлы и убедитесь, что все переменные окружения настроены правильно.

Частые ошибки:
Ошибка базы данных:

Убедитесь, что PostgreSQL запущен и доступен по указанному адресу.
Проверьте строку подключения DATABASE_URL в .env.
Проблемы с миграциями:
```bash
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```
Проблемы с зависимостями:
```bash
pip install --upgrade -r req.txt
```


Спасибо за использование HotLine! Надеемся, что наш проект будет полезен для вас.







