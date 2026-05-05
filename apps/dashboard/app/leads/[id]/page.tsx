import Link from "next/link";
import { apiGet } from "../../../lib/api";

type Detail = {
  business: Record<string, any>;
  audits: Record<string, any>[];
  scores: Record<string, any>[];
  sites: Record<string, any>[];
  messages: Record<string, any>[];
};

export default async function LeadDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const detail = await apiGet<Detail>(`/businesses/${id}`);
  const business = detail.business;
  const latestScore = detail.scores[0];
  const latestAudit = detail.audits[0];

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <div className="kicker">Lead dossier</div>
          <h1>{business.name}</h1>
          <div className="sub">{business.category} in {business.city}, {business.country}</div>
        </div>
        <div className="toolbar"><span className="chip green">{business.lead_state}</span><Link className="button secondary" href="/leads">Back</Link></div>
      </div>

      <div className="grid three">
        <div className="card metric-card"><div className="metric">Opportunity</div><div className="value">{latestScore?.opportunity_score ?? "--"}</div><div className="delta">Lead score</div></div>
        <div className="card metric-card"><div className="metric">Audit</div><div className="value">{latestAudit?.audit_score ?? "--"}</div><div className="delta">Website score</div></div>
        <div className="card metric-card"><div className="metric">Previews</div><div className="value">{detail.sites.length}</div><div className="delta">Generated sites</div></div>
      </div>

      <div className="grid two">
        <div className="card pad">
          <div className="card-header"><div><div className="kicker">Business data</div><h2>Record</h2></div><span className="chip">Public info</span></div>
          <div className="mini-list">
            <div className="mini-item"><span className="small">State</span><strong>{business.lead_state}</strong></div>
            <div className="mini-item"><span className="small">Email</span><strong>{business.email || "none"}</strong></div>
            <div className="mini-item"><span className="small">Website</span><strong>{business.website || "none"}</strong></div>
            <div className="mini-item"><span className="small">Source</span><strong>{business.source_url || "none"}</strong></div>
          </div>
        </div>
        <div className="card pad">
          <div className="card-header"><div><div className="kicker">Latest score</div><h2>Fit analysis</h2></div><span className="chip">MVP scoring</span></div>
          {latestScore ? (
            <div className="status-grid">
              <div className="status-tile"><div className="metric">Need</div><strong>{latestScore.need_score}</strong></div>
              <div className="status-tile"><div className="metric">Contact</div><strong>{latestScore.contactability_score}</strong></div>
              <div className="status-tile"><div className="metric">Value</div><strong>{latestScore.business_value_score}</strong></div>
              <div className="status-tile"><div className="metric">Complexity</div><strong>{latestScore.complexity_score}</strong></div>
            </div>
          ) : <p className="small">No score yet.</p>}
        </div>
      </div>

      <div className="card pad">
        <div className="card-header"><div><div className="kicker">Generated assets</div><h2>Sites</h2></div><span className="chip">Preview links</span></div>
        <table className="table">
          <tbody>
            {detail.sites.map((site) => (
              <tr key={site.id}>
                <td>{site.title}</td>
                <td><span className="badge good">{site.status}</span></td>
                <td>{site.preview_url ? <a className="button secondary" href={site.preview_url} target="_blank" rel="noreferrer">Preview</a> : <span className="small">No preview</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card pad">
        <div className="card-header"><div><div className="kicker">Outreach</div><h2>Messages</h2></div><span className="chip">Transparent copy</span></div>
        <table className="table">
          <tbody>
            {detail.messages.map((message) => (
              <tr key={message.id}>
                <td>{message.subject}</td>
                <td><span className="badge warn">{message.status}</span></td>
                <td className="small">{message.to_address}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
