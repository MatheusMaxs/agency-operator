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

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <h1>{business.name}</h1>
          <div className="sub">{business.category} in {business.city}, {business.country}</div>
        </div>
        <Link className="button secondary" href="/leads">Back</Link>
      </div>
      <div className="grid two">
        <div className="card">
          <h2>Business</h2>
          <p className="small">State: {business.lead_state}</p>
          <p className="small">Email: {business.email || "none"}</p>
          <p className="small">Website: {business.website || "none"}</p>
          <p className="small">Source: {business.source_url || "none"}</p>
        </div>
        <div className="card">
          <h2>Latest Score</h2>
          {detail.scores[0] ? (
            <>
              <div className="value">{detail.scores[0].opportunity_score}</div>
              <p className="small">Need {detail.scores[0].need_score}, contact {detail.scores[0].contactability_score}, value {detail.scores[0].business_value_score}, complexity {detail.scores[0].complexity_score}</p>
            </>
          ) : <p className="small">No score yet.</p>}
        </div>
      </div>
      <div className="card">
        <h2>Sites</h2>
        <table className="table">
          <tbody>
            {detail.sites.map((site) => (
              <tr key={site.id}>
                <td>{site.title}</td>
                <td>{site.status}</td>
                <td>{site.preview_url ? <a className="button secondary" href={site.preview_url} target="_blank">Preview</a> : "No preview"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="card">
        <h2>Messages</h2>
        <table className="table">
          <tbody>
            {detail.messages.map((message) => (
              <tr key={message.id}>
                <td>{message.subject}</td>
                <td>{message.status}</td>
                <td className="small">{message.to_address}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
