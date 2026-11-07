// Compact "day + month" tile used in booking lists.
export function DateTile({ iso }) {
  const date = new Date(iso)

  return (
    <span className="date-tile" aria-hidden="true">
      <span className="date-tile-day">{date.getDate()}</span>
      <span className="date-tile-month">{date.toLocaleDateString('ru-RU', { month: 'short' })}</span>
    </span>
  )
}
