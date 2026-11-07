# RoomBooking

REST API для бронирования переговорных комнат. Пользователи бронируют комнату на интервал времени, отменяют и переносят свои брони; администраторы управляют комнатами и ролями.

Главная задача проекта — **гарантировать, что одну комнату нельзя забронировать дважды на пересекающееся время**, в том числе при одновременных запросах. Как это сделано — в разделе [«Как решена гонка при бронировании»](#как-решена-гонка-при-бронировании).

## Стек

- Python 3.14, FastAPI, Pydantic v2
- SQLAlchemy 2.0 (синхронный), PostgreSQL 17+, Alembic
- JWT (PyJWT), bcrypt
- pytest, pytest-cov
- Docker Compose, GitHub Actions

## Быстрый старт (Docker)

```bash
cp .env.example .env          # при желании сгенерируйте свой SECRET_KEY (см. ниже)
docker compose up --build
```

API: http://localhost:8000, документация Swagger: http://localhost:8000/docs.

При старте контейнер `api` сам применяет миграции (`alembic upgrade head`). У контейнера своя база в volume `db_data`; остановить и удалить её: `docker compose down -v`.

## Локальный запуск

Нужны Python 3.14 и PostgreSQL.

```bash
python -m venv .venv
.venv/Scripts/activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env          # укажите DATABASE_URL своей БД и SECRET_KEY
alembic upgrade head          # схема создаётся только миграциями
uvicorn main:app --reload
```

Сгенерировать `SECRET_KEY` (не короче 32 символов, иначе приложение не стартует):

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Переменные окружения

| Переменная | Обязательна | По умолчанию | Описание |
|---|---|---|---|
| `DATABASE_URL` | да | — | `postgresql+psycopg2://user:pass@host:5432/room_booking` |
| `SECRET_KEY` | да | — | ключ подписи JWT, ≥ 32 символов |
| `ALGORITHM` | нет | `HS256` | алгоритм JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | нет | `30` | срок жизни токена |
| `DB_ECHO` | нет | `false` | логировать SQL-запросы |
| `TEST_DATABASE_URL` | нет | `DATABASE_URL` + `_test` | БД для тестов |

### Первый администратор

Регистрация всегда создаёт обычного пользователя, а роль меняет только администратор. Первого администратора назначьте вручную:

```bash
# Docker
docker compose exec db psql -U postgres -d room_booking -c "UPDATE users SET role = 'ADMIN' WHERE login = 'your_login'"
```

В базе enum хранится по именам (`'ADMIN'`, `'USER'`), в API — значениями (`"admin"`, `"user"`).

## Эндпоинты

Авторизация — заголовок `Authorization: Bearer <access_token>`, токен выдаёт `POST /users/auth/login`.

| Метод | Путь | Доступ | Описание |
|---|---|---|---|
| POST | `/users/auth/register` | все | регистрация (логин без `@`) |
| POST | `/users/auth/login` | все | вход по логину или email, возвращает JWT |
| GET | `/users/me` | пользователь | профиль текущего пользователя |
| PATCH | `/users/{user_id}/role` | админ | сменить роль другому пользователю |
| GET | `/rooms/list?limit=20&offset=0` | все | список комнат с пагинацией |
| GET | `/rooms/{room_id}` | все | комната |
| POST | `/rooms/create` | админ | создать комнату |
| PATCH | `/rooms/change/{room_id}` | админ | изменить переданные поля комнаты |
| DELETE | `/rooms/delete/{room_id}` | админ | удалить комнату |
| GET | `/bookings/` | пользователь | мои брони, по времени начала |
| POST | `/bookings/` | пользователь | забронировать комнату |
| POST | `/bookings/cancel` | пользователь | отменить свою бронь |
| POST | `/bookings/change` | пользователь | перенести свою бронь |

### Правила бронирования

- время передаётся **с часовым поясом** (`2026-11-08T10:00:00Z` или `...+05:00`), без него — `422`; на сервере всё приводится к UTC;
- начало раньше конца, не в прошлом, длительность не больше 5 часов;
- активные брони одной комнаты не пересекаются; брони «встык» (10:00–11:00 и 11:00–12:00) разрешены;
- отменённая бронь освобождает время.

### Коды ошибок

| Код | Когда |
|---|---|
| 400 | неверное время брони (в прошлом, конец раньше начала, дольше 5 часов) |
| 401 | нет токена, токен недействителен или истёк; неверный логин или пароль |
| 403 | недостаточно прав, чужая бронь, попытка админа сменить роль самому себе |
| 404 | комната, бронь или пользователь не найдены |
| 409 | время занято, логин или email заняты, бронь уже отменена, у комнаты есть предстоящие брони |
| 422 | ошибка валидации запроса |

Ответ с ошибкой всегда имеет вид `{"detail": "..."}`.

## Архитектура

```mermaid
flowchart LR
    Client -->|HTTP| Router
    subgraph Модуль users / rooms / bookings
        Router["*_routers.py<br/>HTTP, схемы, зависимости"] --> Service["*_services.py<br/>бизнес-правила"]
        Service --> Repository["*_repositories.py<br/>запросы SQLAlchemy"]
    end
    Repository --> DB[(PostgreSQL)]
    Service -. доменные исключения .-> Handlers["core/handlers.py<br/>исключение → HTTP-код"]
```

```
core/        config (.env), database (engine, сессия), security (JWT, bcrypt),
             dependencies (текущий пользователь/админ), exceptions, handlers
users/       users_models, users_schemas, users_repositories, users_services, users_routers
rooms/       rooms_*  — та же структура
bookings/    bookings_* — та же структура
alembic/     миграции схемы
tests/       unit, services, api, concurrency
```

- Роутеры тонкие: принимают и валидируют запрос, вызывают сервис.
- Сервисы проверяют правила и бросают доменные исключения (`BookingConflictError`, `RoomNotFoundError`, …), не зная про HTTP.
- `core/handlers.py` превращает исключения в HTTP-ответы.
- Репозитории содержат запросы к БД и сами делают `commit()`.

## Как решена гонка при бронировании

**Проблема.** Сервис сначала проверяет, свободно ли время, и только потом вставляет бронь. Два одновременных запроса оба видят «свободно» и оба вставляют — комната забронирована дважды. Тест `tests/concurrency/test_booking_race.py` воспроизводит это стабильно: `threading.Barrier` заставляет оба запроса пройти проверку до вставки.

**Варианты, которые рассматривались:**

| Подход | Почему не он |
|---|---|
| `SELECT ... FOR UPDATE` по пересекающимся броням | не работает: при вставке новой брони блокировать нечего (фантомные строки) |
| `SELECT ... FOR UPDATE` на строке комнаты / `pg_advisory_xact_lock` | работает, но держится на дисциплине кода: любой новый путь записи без блокировки ломает гарантию |
| **EXCLUDE-ограничение в PostgreSQL** | гарантию даёт сама БД — даже ручной `INSERT` не создаст пересечение |

**Решение** (миграция `0003`):

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;
ALTER TABLE bookings ADD CONSTRAINT bookings_no_overlap
  EXCLUDE USING gist (room_id WITH =, tstzrange(start_time, end_time, '[)') WITH &&)
  WHERE (status = 'ACTIVE');
```

- `[)` — интервал включает начало и не включает конец, поэтому брони «встык» не конфликтуют;
- `WHERE status = 'ACTIVE'` — отменённые брони не мешают;
- проверка в сервисе осталась: она даёт понятный ответ в обычном случае, а ограничение страхует при гонке.

**Две ошибки PostgreSQL, которые означают «время занято»** (`save_without_overlap` в `bookings/bookings_services.py` превращает обе в `409`):

- `23P01 exclusion_violation` — вставка пересекается с уже закоммиченной бронью;
- `40P01 deadlock_detected` — две пересекающиеся вставки одновременно ждут друг друга, и PostgreSQL прерывает одну из них. Тест гонки ловил это примерно в половине прогонов; других блокировок у таблицы броней нет, поэтому deadlock здесь означает именно пересечение.

## База данных и миграции

Схема создаётся и меняется только через Alembic (`Base.metadata.create_all` не используется).

| Ревизия | Что делает |
|---|---|
| `0001` | исходная схема (повторяет базу, созданную раньше через `create_all`) |
| `0002` | время броней — `timestamptz`, `UNIQUE` на `login` и `email`, `users.role` — enum, индекс `bookings.user_id` |
| `0003` | `btree_gist` и ограничение `bookings_no_overlap` |
| `0004` | `ON DELETE CASCADE` для `bookings.room_id` |

```bash
alembic upgrade head      # применить
alembic downgrade -1      # откатить последнюю
alembic check             # модели совпадают со схемой?
```

## Тесты

Тестам нужен PostgreSQL (SQLite не поддерживает EXCLUDE-ограничения). При каждом запуске пересоздаётся отдельная БД `<имя>_test` и к ней применяются те же миграции. Если имя тестовой БД не заканчивается на `_test`, тесты не запустятся — рабочая база не пострадает.

```bash
pytest                          # все тесты
pytest -m unit                  # без БД
pytest -m "services or api"     # сервисы и HTTP
pytest -m concurrency           # гонки
pytest --cov                    # с покрытием (порог 80%, см. .coveragerc)
```

| Папка | Что проверяет |
|---|---|
| `tests/unit` | `validate_time`: границы, прошлое, 5 часов, часовые пояса |
| `tests/services` | бронирование, перенос, отмена; ограничение БД без проверки сервиса; дубли пользователей |
| `tests/api` | все эндпоинты через `TestClient`: права, коды ответов, токены |
| `tests/concurrency` | параллельное создание и перенос броней в один слот — сохраняется ровно одна |

Каждый тест работает в транзакции, которая откатывается в конце (`join_transaction_mode="create_savepoint"`), поэтому `commit()` в репозиториях не мешает изоляции. Тесты гонок используют отдельные сессии с настоящими коммитами и очищают таблицы после себя.

## CI

`.github/workflows/tests.yml` на каждый push и pull request поднимает PostgreSQL 17 и запускает `pytest --cov`.

Тот же сценарий можно прогнать локально на Linux без GitHub:

```bash
docker network create rb-ci
docker run -d --name rb-ci-db --network rb-ci -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=room_booking postgres:17
docker run --rm --network rb-ci -v "$(pwd):/src:ro" -w /src \
  -e DATABASE_URL=postgresql+psycopg2://postgres:postgres@rb-ci-db:5432/room_booking \
  -e TEST_DATABASE_URL=postgresql+psycopg2://postgres:postgres@rb-ci-db:5432/room_booking_test \
  -e SECRET_KEY=ci-only-secret-key-that-is-long-enough \
  -e PYTHONDONTWRITEBYTECODE=1 -e COVERAGE_FILE=/tmp/.coverage \
  python:3.14-slim sh -c "pip install -q -r requirements-dev.txt && pytest -p no:cacheprovider --cov"
docker rm -f rb-ci-db && docker network rm rb-ci
```

В Git Bash на Windows перед командами выполните `export MSYS_NO_PATHCONV=1` и используйте `$(pwd -W)` вместо `$(pwd)`.

## Решения и компромиссы

- **Удаление комнаты.** Если у комнаты есть активные брони, которые ещё не закончились, удаление запрещено (`409`). Прошлые и отменённые брони удаляются вместе с комнатой (`ON DELETE CASCADE`) — история по удалённой комнате не сохраняется.
- **Транзакции в репозиториях.** `commit()` вызывается внутри репозиториев, поэтому одна запись — одна транзакция. Сейчас операций из нескольких записей нет, и этого достаточно; ошибки БД при коммите (`23P01`, `40P01`, `UNIQUE`) обрабатываются в сервисах вокруг вызова репозитория.
- **Одинаковый ответ при входе.** Неизвестный логин и неверный пароль возвращают один и тот же `401`, чтобы по ответу нельзя было узнать, существует ли пользователь.
- **Без кэша.** Список комнат — дешёвый запрос к маленькой таблице; Redis добавил бы сервис и риск устаревших данных без измеримой пользы.
- **Без refresh-токенов.** Токен живёт 30 минут, после истечения клиент заново входит.
- **Отмена и перенос через `POST`.** `POST /bookings/cancel` и `POST /bookings/change` оставлены как есть, без перехода на `PATCH /bookings/{id}`.
