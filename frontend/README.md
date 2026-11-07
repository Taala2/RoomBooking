# RoomBooking — frontend

React 19 + Vite, JavaScript. Из зависимостей только `react-router-dom`; стили — обычный CSS (`src/index.css`), светлая и тёмная тема по настройке системы.

## Запуск

```bash
cp .env.example .env     # VITE_API_URL — адрес backend, без пути (http://host:port)
npm install
npm run dev              # http://localhost:5173
```

В `.env` backend должно быть `CORS_ORIGINS=["http://localhost:5173"]`.

```bash
npm run lint             # oxlint
npm run build            # сборка в dist/
```

## Структура

```
src/
  api/          client.js — fetch, токен, ошибки API; auth, rooms, bookings, users — вызовы эндпоинтов
  context/      AuthContext — текущий пользователь, вход/выход, useAuth()
  hooks/        useAsync — загрузка данных с защитой от устаревших ответов
  utils/        dates — локальное время ↔ ISO UTC, проверка интервала брони
  components/   Header, ProtectedRoute, DaySchedule, TimeRangeForm, RoomForm, ErrorMessage, ErrorBoundary
  pages/        RoomsPage, RoomPage, MyBookingsPage, LoginPage, RegisterPage
  pages/admin/  AdminRoomsPage, AdminUsersPage
```

## Решения

- **Время.** Пользователь вводит локальные дату и время, в API уходит ISO в UTC (`toISOString()`), отображается снова в локальном времени.
- **Проверки в формах** повторяют правила backend (длина логина, 5 часов, не в прошлом), чтобы сразу показать понятную ошибку; окончательное решение всегда за backend — его `detail` выводится под формой.
- **Токен** хранится в `localStorage`. Это просто и достаточно для учебного проекта, но уязвимо к XSS: в продакшене лучше httpOnly-cookie. При ответе `401` на запрос с токеном пользователь автоматически выходит.
- **Права в интерфейсе** (скрытые пункты меню, `ProtectedRoute adminOnly`) — только удобство; доступ проверяет backend.
