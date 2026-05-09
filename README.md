# 🌤️ WeatherASM - Weather Analysis & Forecasting Backend

Добро пожаловать! Это REST API для анализа и прогнозирования погоды, построенное на **FastAPI + PostgreSQL**, с данными от **Open-Meteo** (бесплатно, без API-ключа).

## 🛠 Технологический стек

| Компонент | Технология |
| --- | --- |
| Язык | Python 3.11+ |
| Фреймворк | FastAPI + Uvicorn |
| База данных | PostgreSQL 15 |
| ORM | SQLAlchemy 2.0 |
| Аутентификация | JWT (python-jose, passlib, bcrypt) |
| Источник данных | Open-Meteo API (free, no key) |
| Контейнеризация | Docker + Docker Compose |

---

## 🚀 Быстрый старт

### 1. Клонирование и настройка

```bash
git clone <repo-url>
cd weather-backend
cp .env.example .env
# Отредактируйте .env под ваши настройки
```

### 2. Запуск через Docker (рекомендуется)

```bash
docker-compose up --build
```

### 3. Локальная разработка (без Docker)

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload
```

После запуска Swagger UI будет доступен по адресу:
👉 **<http://127.0.0.1:8000/docs>**

---

## 📡 API Endpoints

### 🔐 Аутентификация (`/auth`)

| Метод | URL | Описание |
| --- | --- | --- |
| POST | `/auth/register` | Регистрация нового пользователя |
| POST | `/auth/login` | Вход (получить JWT) |
| POST | `/auth/refresh` | Обновить access token |

### 👤 Пользователи (`/users`)

| Метод | URL | Доступ |
| --- | --- | --- |
| GET | `/users/me` | Мой профиль |
| PUT | `/users/me` | Обновить профиль |
| POST | `/users/me/change-password` | Сменить пароль |
| DELETE | `/users/me` | Удалить аккаунт |
| GET | `/users/` | Список всех (admin) |
| GET | `/users/{id}/` | Подробности о пользователе |
| PATCH | `/users/{id}/deactivate` | Деактивировать (admin) |

### 📍 Сохранённые локации (`/locations`)

| Метод | URL | Описание |
| --- | --- | --- |
| GET | `/locations/` | Мои сохранённые города |
| POST | `/locations/` | Добавить город |
| DELETE | `/locations/{id}` | Удалить город |

### 🌡️ Погода (`/weather`)

| Метод | URL | Описание |
| --- | --- | --- |
| GET | `/weather/current?city=Vilnius` | Текущая погода |
| GET | `/weather/forecast?city=Vilnius&days=7` | Прогноз на 7–16 дней |
| GET | `/weather/alerts?city=Vilnius` | Предупреждения об опасной погоде |
| GET | `/weather/history?city=Vilnius` | История запросов |
| GET | `/weather/analysis?city=Vilnius&days=30` | Статистический анализ |
| GET | `/weather/compare?cities=Vilnius,Warsaw,Riga` | Сравнение городов |

---

## ⚠️ Пороги оповещений

| Тип | Порог |
| --- | --- |
| Сильный ветер | ≥ 60 km/h |
| Сильный дождь | ≥ 20 mm |
| Сильный снегопад | ≥ 10 cm |
| Сильная жара | ≥ 35°C |
| Сильный мороз | ≤ −15°C |
| Гроза | WMO код 95/96/99 |

---

## 📊 Генерация ERD

```bash
python gen_erd.py
# Создаёт diagram.png
```

## 🐳 Только Docker (без compose)

```bash
docker build -t weather-backend .
docker run -p 8000:8000 --env-file .env weather-backend
```
