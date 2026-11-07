# RoomBooking — frontend

React 19 + Vite, JavaScript. Зависимости: `react-router-dom`, `lucide-react` (иконки), `@fontsource-variable/inter` (шрифт Inter, хранится в проекте — работает без интернета и в Docker). Стили — обычный CSS без UI-кита, только светлая тема.

Дизайн — SaaS-дашборд: боковое меню (на планшете и телефоне — выезжающее по кнопке), шапка с названием страницы и пользователем, белые карточки на светлом фоне. Основной цвет `#4F46E5` — только для главных кнопок, активного пункта меню и важных действий; статусы броней — небольшие метки на мягком фоне.

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
  utils/        dates — локальное время ↔ ISO UTC; bookings — состояние брони (активна/завершена/отменена)
  styles/       tokens (палитра, шрифт), components, layout, pages
  components/   AppLayout, AuthLayout, Sidebar, Header — каркас;
                Button (default/hover/active/disabled/loading), StatusBadge, DateTile, States (загрузка, пусто),
                DaySchedule, TimeRangeForm, RoomForm, ErrorMessage, ProtectedRoute, ErrorBoundary
  pages/        DashboardPage, RoomsPage, RoomPage, MyBookingsPage, LoginPage, RegisterPage
  pages/admin/  AdminRoomsPage, AdminUsersPage
```

Все цвета, радиусы и размеры шрифта — переменные в `src/styles/tokens.css`. Мелкий вторичный текст — `#6B7280` вместо `#858B98` из концепции: так он проходит требование контраста WCAG; `#858B98` используется для иконок и подписей шкалы.

## Решения

- **Время.** Пользователь вводит локальные дату и время, в API уходит ISO в UTC (`toISOString()`), отображается снова в локальном времени.
- **Проверки в формах** повторяют правила backend (длина логина, 5 часов, не в прошлом), чтобы сразу показать понятную ошибку; окончательное решение всегда за backend — его `detail` выводится под формой.
- **Токен** хранится в `localStorage`. Это просто и достаточно для учебного проекта, но уязвимо к XSS: в продакшене лучше httpOnly-cookie. При ответе `401` на запрос с токеном пользователь автоматически выходит.
- **Права в интерфейсе** (скрытые пункты меню, `ProtectedRoute adminOnly`) — только удобство; доступ проверяет backend.
