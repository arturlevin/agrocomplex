# Агрокомплекс — учёт тепличного хозяйства

Небольшое приложение для учёта работы тепличного комплекса: теплицы, культуры, график
работ (посев / полив / удобрение / сбор урожая), фактическое выполнение работ и расход
ресурсов. Делалось как учебный проект (летняя практика).

Стек: FastAPI + PostgreSQL на бэкенде, Vue 3 + Element Plus на фронтенде.

## Роли

- **Главный агроном** — заводит теплицы, культуры, ресурсы и сотрудников, составляет график работ.
- **Агроном** — видит свои задачи и вносит фактическое выполнение (дату, расход ресурсов, урожай).

## Запуск

Бэкенд и база — через Docker, фронтенд — локально через `npm run dev` (так удобнее
для разработки и не зависит от того, достаётся ли Docker до npm-реестра).

**1. Бэкенд и база данных:**

```bash
docker compose up --build
```

- API: http://localhost:8000 (документация — http://localhost:8000/docs)

При первом запуске бэкенд сам создаёт таблицы и добавляет тестовые данные (см. `backend/app/seed.py`):

| Email | Пароль | Роль |
|---|---|---|
| chief@agrocomplex.ru | chief123 | Главный агроном |
| petrov@agrocomplex.ru | agro123 | Агроном |
| sidorova@agrocomplex.ru | agro123 | Агроном |

**2. Фронтенд** (в отдельном терминале):

```bash
cd frontend
npm install
npm run dev
```

- Фронтенд: http://localhost:5173, сам стучится в http://localhost:8000 (см. `VITE_API_URL` в `src/api/http.js`).

Если нужно собрать фронтенд тоже в Docker (например, для прод-сборки) — в `frontend/Dockerfile`
уже есть многоступенчатая сборка с nginx, достаточно вернуть сервис `frontend` в `docker-compose.yml`.

## Запуск бэкенда без Docker

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # и поправить DATABASE_URL, если Postgres не в докере
uvicorn app.main:app --reload
```

## Структура

```
backend/app/
  models.py       — таблицы (SQLAlchemy)
  schemas.py       — Pydantic-схемы запросов/ответов
  routers/          — эндпоинты по сущностям
  security.py       — хэширование паролей и JWT
  deps.py            — текущий пользователь / проверка роли
  seed.py             — тестовые данные при первом запуске

frontend/src/
  views/         — страницы (по одной на раздел меню)
  store/auth.js   — состояние авторизации (Pinia)
  api/http.js      — axios-клиент с подстановкой токена
```
