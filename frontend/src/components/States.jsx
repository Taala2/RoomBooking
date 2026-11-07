import { LoaderCircle } from 'lucide-react'

export function LoadingState({ text = 'Загрузка…', inline = false }) {
  return (
    <div className={`state ${inline ? 'state-inline' : ''}`} role="status">
      <LoaderCircle size={18} className="spinner" aria-hidden="true" />
      <span>{text}</span>
    </div>
  )
}

// icon: Lucide component; action: optional element (e.g. a link or button).
export function EmptyState({ icon: Icon, title, text, action }) {
  return (
    <div className="state">
      {Icon && (
        <span className="icon-tile" aria-hidden="true">
          <Icon size={20} />
        </span>
      )}
      <p className="state-title">{title}</p>
      {text && <p className="small">{text}</p>}
      {action}
    </div>
  )
}
