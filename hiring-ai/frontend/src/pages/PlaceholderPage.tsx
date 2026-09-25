import { Link } from 'react-router-dom'

type PlaceholderPageProps = {
  title: string
  summary: string
  cta?: { to: string; label: string }
}

export function PlaceholderPage({ title, summary, cta }: PlaceholderPageProps) {
  return (
    <div className="ops-workspace">
      <header className="ops-workspace__header">
        <p className="ops-kicker">Coming online</p>
        <h1>{title}</h1>
        <p className="ops-lead">{summary}</p>
      </header>
      <div className="ops-banner" role="note">
        This screen is part of the Hiring AI operating shell. Core hire actions live in Jobs,
        Candidates, Sourcing, Match, and Settings.
      </div>
      {cta ? (
        <p>
          <Link className="ops-queue-card__action" to={cta.to}>
            {cta.label}
          </Link>
        </p>
      ) : null}
    </div>
  )
}
