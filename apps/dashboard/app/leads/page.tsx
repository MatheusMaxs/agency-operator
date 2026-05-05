import Link from "next/link";
import { apiGet } from "../../lib/api";

type Business = {
  id: number;
  name: string;
  category: string | null;
  city: string | null;
  country: string | null;
  email: string | null;
  website: string | null;
  lead_state: string;
  created_at: string;
};

function badgeClass(state: string) {
  if (["QUALIFIED", "SITE_DEPLOYED", "CONTACT_READY", "PAYMENT_LINK_SENT", "PAID"].includes(state)) return "badge good";
  if (["FAILED", "DO_NOT_CONTACT", "REJECTED"].includes(state)) return "badge bad";
  return "badge warn";
}

export default async function LeadsPage() {
  const businesses = await apiGet<Business[]>("/businesses?limit=200");
  const qualified = businesses.filter((business) => business.lead_state === "QUALIFIED").length;
  const paid = businesses.filter((business) => business.lead_state === "PAID").length;
  const contactReady = businesses.filter((business) => ["CONTACT_READY", "CONTACTED", "PAYMENT_LINK_SENT"].includes(business.lead_state)).length;

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <div className="kicker">Lead intelligence</div>
          <h1>European leads</h1>
          <div className="sub">Public business records imported, scored, and staged for preview generation and transparent outreach.</div>
        </div>
        <div className="toolbar">
          <span className="chip green">{businesses.length} records</span>
          <span className="chip">{qualified} qualified</span>
          <span className="chip">{paid} paid</span>
        </div>
      </div>

      <div className="grid three">
        <div className="card metric-card"><div className="metric">Discovered</div><div className="value">{businesses.length}</div><div className="delta">Hermes import queue</div></div>
        <div className="card metric-card"><div className="metric">Sales-ready</div><div className="value">{contactReady}</div><div className="delta">Outreach pipeline</div></div>
        <div className="card metric-card"><div className="metric">Closed</div><div className="value">{paid}</div><div className="delta">Kiwify paid state</div></div>
      </div>

      <div className="card pad">
        <div className="card-header">
          <div>
            <div className="kicker">Pipeline table</div>
            <h2>Business records</h2>
          </div>
          <span className="chip">Limit 200</span>
        </div>
        <table className="table">
          <thead><tr><th>Name</th><th>Location</th><th>Contact</th><th>State</th><th></th></tr></thead>
          <tbody>
            {businesses.map((business) => (
              <tr key={business.id}>
                <td><strong>{business.name}</strong><div className="small">{business.category || "Unknown category"}</div></td>
                <td>{business.city || "Unknown"}, {business.country || "EU"}</td>
                <td><div className="small">{business.email || "No email"}</div><div className="small">{business.website || "No website"}</div></td>
                <td><span className={badgeClass(business.lead_state)}>{business.lead_state}</span></td>
                <td><Link className="button secondary" href={`/leads/${business.id}`}>Open</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
