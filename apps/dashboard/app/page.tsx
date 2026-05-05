import { apiGet } from "../lib/api";

type Overview = {
  businesses: number;
  qualified: number;
  sites: number;
  contacts_sent: number;
  approvals_pending: number;
  actions: number;
  revenue_eur: number;
};

export default async function Page() {
  const overview = await apiGet<Overview>("/metrics/overview");

  const metrics = [
    ["Revenue EUR", overview.revenue_eur.toFixed(2)],
    ["Businesses", overview.businesses],
    ["Qualified", overview.qualified],
    ["Sites", overview.sites],
    ["Contacts sent", overview.contacts_sent],
    ["Pending approvals", overview.approvals_pending],
    ["Logged actions", overview.actions],
  ];

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <h1>Operator Overview</h1>
          <div className="sub">Start small, log everything, approve outreach before sending.</div>
        </div>
      </div>
      <div className="grid">
        {metrics.map(([label, value]) => (
          <div className="card" key={label}>
            <div className="metric">{label}</div>
            <div className="value">{value}</div>
          </div>
        ))}
      </div>
      <div className="grid two">
        <div className="card">
          <h2>Safe MVP Mode</h2>
          <p className="small">Email dry-run and manual approvals are enabled by default. This prevents accidental spam and keeps the first campaign reviewable.</p>
        </div>
        <div className="card">
          <h2>First Flow</h2>
          <p className="small">Discover demo leads, audit, score, generate a preview, deploy it through API preview, prepare outreach, approve, then dry-run send.</p>
        </div>
      </div>
    </div>
  );
}
