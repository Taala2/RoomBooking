import { LoaderCircle } from 'lucide-react'

const ICON_SIZE = 16

// variant: primary | secondary | danger | ghost; size: md | sm.
// loading shows a spinner, keeps the label and blocks repeated clicks.
export function Button({
  variant = 'secondary',
  size = 'md',
  icon: Icon,
  loading = false,
  block = false,
  iconOnly = false,
  className = '',
  type = 'button',
  disabled,
  children,
  ...rest
}) {
  const classes = [
    'button',
    variant !== 'secondary' && `button-${variant}`,
    size === 'sm' && 'button-sm',
    block && 'button-block',
    iconOnly && 'button-icon',
    className,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <button type={type} className={classes} disabled={disabled || loading} aria-busy={loading || undefined} {...rest}>
      {loading ? (
        <LoaderCircle size={ICON_SIZE} className="spinner" aria-hidden="true" />
      ) : (
        Icon && <Icon size={ICON_SIZE} aria-hidden="true" />
      )}
      {iconOnly ? <span className="visually-hidden">{children}</span> : children}
    </button>
  )
}
