import { apiGet } from "../lib/api";

type Overview = {
  businesses: number;
  qualified: number;
  sites: number;
  contacts_sent: number;
  approvals_pending: number;
  actions: number;
  revenue_eur: number;
  mrr_eur: number;
  paid_customers: number;
};

function eur(value: number) {
  return `EUR ${Math.round(value).toLocaleString("en-US")}`;
}

function pct(value: number, max: number) {
  if (max <= 0) return 0;
  return Math.max(7, Math.min(100, Math.round((value / max) * 100)));
}

export default async function Page() {
  const overview = await apiGet<Overview>("/metrics/overview");
  const target = 10000;
  const projected = overview.revenue_eur + Math.max(overview.sites - overview.paid_customers, 0) * 1000;
  const targetPercent = Math.max(0, Math.min(100, Math.round((overview.revenue_eur / target) * 100)));
  const maxPipeline = Math.max(overview.businesses, overview.qualified, overview.sites, overview.contacts_sent, overview.paid_customers, 1);
  const pipeline = [
    { label: "Leads", count: overview.businesses, amount: overview.businesses * 1000, tone: "" },
    { label: "Qualified", count: overview.qualified, amount: overview.qualified * 1000, tone: "amber" },
    { label: "Previews", count: overview.sites, amount: overview.sites * 1000, tone: "violet" },
    { label: "Paid", count: overview.paid_customers, amount: overview.revenue_eur, tone: "" },
  ];
  const metrics = [
    { label: "Closed revenue", value: eur(overview.revenue_eur), delta: `${targetPercent}% of 10k target` },
    { label: "Care plan MRR", value: eur(overview.mrr_eur), delta: "49-149 EUR per client" },
    { label: "Paid clients", value: overview.paid_customers.toString(), delta: "Goal: 10 closes" },
    { label: "Pending approvals", value: overview.approvals_pending.toString(), delta: "Manual gates" },
  ];
  const heat = Array.from({ length: 90 }, (_, index) => (index * 7 + overview.actions + overview.businesses) % 13);
  const bars = [38, 54, 42, 74, 61, 82, 49, 58, 77, 69, 88, 72];

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <div className="kicker">AI agency operator / Europe</div>
          <h1>Revenue control room</h1>
          <div className="sub">Track the full month-one machine: lead discovery, previews, outreach, Kiwify payments, Vercel deploys, and recurring care plans.</div>
        </div>
        <div className="toolbar">
          <span className="chip green">Target EUR 10k</span>
          <span className="chip">NVIDIA build</span>
          <span className="chip">Kiwify</span>
          <span className="chip">Vercel</span>
        </div>
      </div>

      <section className="hero-grid">
        <div className="card profit-panel">
          <div className="profit-top">
            <div>
              <div className="kicker">Projected profit</div>
              <div className="profit-title">Month one pipeline</div>
            </div>
            <div className="profit-number"><span>/</span> {eur(projected)}</div>
          </div>

          <div className="profit-meta">
            <span className="chip">Date: live</span>
            <span className="chip">Status: approvals on</span>
            <span className="chip">Withdrawals: manual</span>
          </div>

          <div className="pipeline-bars">
            {pipeline.map((item) => (
              <div className="pipeline-row" key={item.label}>
                <div className="pipeline-label">{item.label}</div>
                <div className="pipeline-track">
                  <div className={item.tone ? `pipeline-fill ${item.tone}` : "pipeline-fill"} style={{ width: `${pct(item.count, maxPipeline)}%` }} />
                </div>
                <div className="pipeline-amount">{item.count} / {eur(item.amount)}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="stack">
          <div className="card lead-spotlight">
            <div className="kicker">New leads</div>
            <h2>European local businesses</h2>
            <div className="value">{overview.businesses}</div>
            <div className="small">Prospects imported by Hermes/browser-use and scored for website opportunity.</div>
            <div className="lead-progress" aria-label="Lead progress"><span /></div>
          </div>

          <div className="card source-panel">
            <div className="card-header">
              <div>
                <div className="kicker">Lead source</div>
                <h2>{overview.qualified}</h2>
                <div className="small">qualified this cycle</div>
              </div>
              <span className="badge good">+ pipeline</span>
            </div>
            <div className="source-bars">
              <div className="source-row"><span>Organic</span><div className="source-track"><span style={{ width: "74%" }} /></div><span>74%</span></div>
              <div className="source-row"><span>Maps</span><div className="source-track"><span style={{ width: "58%" }} /></div><span>58%</span></div>
              <div className="source-row"><span>Email</span><div className="source-track"><span style={{ width: "42%" }} /></div><span>42%</span></div>
            </div>
            <div className="mini-list">
              <div className="mini-item"><span className="small">Previews generated</span><strong>{overview.sites}</strong></div>
              <div className="mini-item"><span className="small">Contacts sent</span><strong>{overview.contacts_sent}</strong></div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid">
        {metrics.map((metric) => (
          <div className="card metric-card" key={metric.label}>
            <div className="metric">{metric.label}</div>
            <div className="value">{metric.value}</div>
            <div className="delta">{metric.delta}</div>
          </div>
        ))}
      </section>

      <section className="grid two">
        <div className="card pad">
          <div className="card-header">
            <div>
              <div className="kicker">Conversion curve</div>
              <h2>Outreach to close velocity</h2>
            </div>
            <span className="chip">Live report</span>
          </div>
          <div className="chart-wrap">
            <svg className="chart-svg" viewBox="0 0 640 240" role="img" aria-label="Conversion curve chart">
              <defs>
                <linearGradient id="greenArea" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#69ef7b" stopOpacity="0.36" />
                  <stop offset="100%" stopColor="#69ef7b" stopOpacity="0" />
                </linearGradient>
              </defs>
              {[40, 80, 120, 160, 200].map((y) => <line className="chart-grid" key={y} x1="0" x2="640" y1={y} y2={y} />)}
              {[80, 160, 240, 320, 400, 480, 560].map((x) => <line className="chart-grid" key={x} x1={x} x2={x} y1="0" y2="240" />)}
              <path className="chart-area" d="M0 190 C70 174 82 139 140 151 C210 166 214 90 286 112 C342 130 358 58 430 76 C512 98 524 32 640 46 L640 240 L0 240 Z" />
              <path className="chart-line" d="M0 190 C70 174 82 139 140 151 C210 166 214 90 286 112 C342 130 358 58 430 76 C512 98 524 32 640 46" />
            </svg>
          </div>
        </div>

        <div className="card pad">
          <div className="card-header">
            <div>
              <div className="kicker">Activity heatmap</div>
              <h2>Agent actions</h2>
            </div>
            <span className="chip">{overview.actions} logged</span>
          </div>
          <div className="heatmap" aria-label="Agent action heatmap">
            {heat.map((value, index) => (
              <span className={value > 9 ? "heat-cell c" : value > 5 ? "heat-cell b" : value > 2 ? "heat-cell a" : "heat-cell"} key={index} />
            ))}
          </div>
          <div className="status-grid">
            <div className="status-tile"><div className="metric">Safe mode</div><strong>Approval gates</strong><div className="small">First outreach stays reviewable.</div></div>
            <div className="status-tile"><div className="metric">Payment ops</div><strong>Kiwify links</strong><div className="small">Created after clear interest only.</div></div>
          </div>
        </div>
      </section>

      <section className="grid three">
        <div className="card pad">
          <div className="kicker">Care plans</div>
          <h2>MRR engine</h2>
          <div className="bar-row">
            {bars.map((height, index) => <span className={index > 7 ? "bar hot" : "bar"} key={index} style={{ height: `${height}%` }} />)}
          </div>
        </div>
        <div className="card pad">
          <div className="kicker">First flow</div>
          <h2>Discovery to payment</h2>
          <div className="mini-list">
            {[
              "Import public leads",
              "Audit weak web presence",
              "Generate preview",
              "Deploy Vercel/API preview",
              "Send transparent outreach",
              "Create Kiwify link",
            ].map((item, index) => <div className="mini-item" key={item}><span>{item}</span><strong>{String(index + 1).padStart(2, "0")}</strong></div>)}
          </div>
        </div>
        <div className="card pad">
          <div className="kicker">System mix</div>
          <h2>Model stack</h2>
          <div className="status-grid">
            <div className="status-tile"><div className="metric">AI</div><strong>NVIDIA</strong></div>
            <div className="status-tile"><div className="metric">Deploy</div><strong>Vercel</strong></div>
            <div className="status-tile"><div className="metric">Pay</div><strong>Kiwify</strong></div>
            <div className="status-tile"><div className="metric">Ops</div><strong>Hermes</strong></div>
          </div>
        </div>
      </section>
    </div>
  );
}
