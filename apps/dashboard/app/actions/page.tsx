import { apiGet } from "../../lib/api";

type AgentAction = {
  id: number;
  agent_name: string;
  action_type: string;
  target_type: string | null;
  target_id: string | null;
  status: string;
  error_message: string | null;
  estimated_cost_eur: string;
  created_at: string;
};

export default async function ActionsPage() {
  const actions = await apiGet<AgentAction[]>("/agent-actions?limit=200");
  const failed = actions.filter((action) => action.status === "failed").length;
  const completed = actions.filter((action) => action.status === "completed").length;

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <div className="kicker">Audit trail</div>
          <h1>Agent actions</h1>
          <div className="sub">Every tool call leaves a trace so Hermes and operators can be reviewed safely.</div>
        </div>
        <div className="toolbar"><span className="chip green">{completed} completed</span><span className="chip">{failed} failed</span></div>
      </div>

      <div className="card pad">
        <div className="card-header"><div><div className="kicker">System log</div><h2>Recent operations</h2></div><span className="chip">Limit 200</span></div>
        <table className="table">
          <thead><tr><th>ID</th><th>Agent</th><th>Action</th><th>Target</th><th>Status</th><th>Error</th></tr></thead>
          <tbody>
            {actions.map((action) => (
              <tr key={action.id}>
                <td className="mono">#{action.id}</td>
                <td>{action.agent_name}</td>
                <td>{action.action_type}</td>
                <td className="small">{action.target_type || "-"} {action.target_id || ""}</td>
                <td><span className={action.status === "completed" ? "badge good" : action.status === "failed" ? "badge bad" : "badge warn"}>{action.status}</span></td>
                <td className="small">{action.error_message || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
