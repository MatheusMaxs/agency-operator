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
  if (["QUALIFIED", "SITE_DEPLOYED", "CONTACT_READY", "PAID"].includes(state)) return "badge good";
  if (["FAILED", "DO_NOT_CONTACT", "REJECTED"].includes(state)) return "badge bad";
  return "badge warn";
}

export default async function LeadsPage() {
  const businesses = await apiGet<Business[]>("/businesses?limit=200");
  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <h1>Leads</h1>
          <div className="sub">Businesses discovered, scored, and prepared for previews.</div>
        </div>
      </div>
      <div className="card">
        <table className="table">
          <thead><tr><th>Name</th><th>Location</th><th>Contact</th><th>State</th><th></th></tr></thead>
          <tbody>
            {businesses.map((business) => (
              <tr key={business.id}>
                <td><strong>{business.name}</strong><div className="small">{business.category || "Unknown category"}</div></td>
                <td>{business.city}, {business.country}</td>
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
