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
  const deployed = sites.filter((site) => site.status === "DEPLOYED").length;
  const avgQuality = sites.length ? Math.round(sites.reduce((sum, site) => sum + site.quality_score, 0) / sites.length) : 0;

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <div className="kicker">Preview factory</div>
          <h1>Generated sites</h1>
          <div className="sub">AI-assisted local business previews ready for Vercel or API-hosted review links.</div>
        </div>
        <div className="toolbar">
          <span className="chip green">{deployed} deployed</span>
          <span className="chip">{avgQuality} avg quality</span>
        </div>
      </div>

      <div className="grid three">
        <div className="card metric-card"><div className="metric">Total previews</div><div className="value">{sites.length}</div><div className="delta">Generated assets</div></div>
        <div className="card metric-card"><div className="metric">Deployed</div><div className="value">{deployed}</div><div className="delta">Vercel/API preview</div></div>
        <div className="card metric-card"><div className="metric">Quality score</div><div className="value">{avgQuality}</div><div className="delta">MVP estimator</div></div>
      </div>

      <div className="card pad">
        <div className="card-header"><div><div className="kicker">Preview ledger</div><h2>Site deployments</h2></div><span className="chip">Public links</span></div>
        <table className="table">
          <thead><tr><th>Site</th><th>Business</th><th>Status</th><th>Quality</th><th>Preview</th></tr></thead>
          <tbody>
            {sites.map((site) => (
              <tr key={site.id}>
                <td>{site.title}</td>
                <td>{site.business_name}</td>
                <td><span className="badge good">{site.status}</span></td>
                <td>{site.quality_score}</td>
                <td>{site.preview_url ? <a className="button secondary" href={site.preview_url} target="_blank" rel="noreferrer">Open</a> : <span className="small">None</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
