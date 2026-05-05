import { apiGet } from "../../lib/api";

type Site = {
  id: number;
  business_id: number;
  business_name: string;
  status: string;
  title: string;
  preview_url: string | null;
  quality_score: number;
  created_at: string;
};

export default async function SitesPage() {
  const sites = await apiGet<Site[]>("/generated-sites");
  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <h1>Sites</h1>
          <div className="sub">Generated previews attached to leads.</div>
        </div>
      </div>
      <div className="card">
        <table className="table">
          <thead><tr><th>Site</th><th>Business</th><th>Status</th><th>Quality</th><th>Preview</th></tr></thead>
          <tbody>
            {sites.map((site) => (
              <tr key={site.id}>
                <td>{site.title}</td>
                <td>{site.business_name}</td>
                <td><span className="badge good">{site.status}</span></td>
                <td>{site.quality_score}</td>
                <td>{site.preview_url ? <a className="button secondary" href={site.preview_url} target="_blank">Open</a> : "None"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
