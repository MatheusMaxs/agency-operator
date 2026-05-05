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
  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <h1>Agent Actions</h1>
          <div className="sub">Every tool call should leave an audit trail.</div>
        </div>
      </div>
      <div className="card">
        <table className="table">
          <thead><tr><th>ID</th><th>Agent</th><th>Action</th><th>Target</th><th>Status</th><th>Error</th></tr></thead>
          <tbody>
            {actions.map((action) => (
              <tr key={action.id}>
                <td>{action.id}</td>
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
