import { apiGet } from "../../lib/api";
import { approveAction, rejectAction } from "./actions";

type Approval = {
  id: number;
  approval_type: string;
  target_type: string;
  target_id: number;
  status: string;
  reason: string | null;
  created_at: string;
};

export default async function ApprovalsPage() {
  const approvals = await apiGet<Approval[]>("/approvals");
  const pending = approvals.filter((approval) => approval.status === "PENDING").length;
  const approved = approvals.filter((approval) => approval.status === "APPROVED").length;

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <div className="kicker">Safety gates</div>
          <h1>Approvals</h1>
          <div className="sub">Manual review points before sensitive actions such as first outreach and customer-facing messages.</div>
        </div>
        <div className="toolbar"><span className="chip green">{pending} pending</span><span className="chip">{approved} approved</span></div>
      </div>

      <div className="card pad">
        <div className="card-header"><div><div className="kicker">Control queue</div><h2>Manual decisions</h2></div><span className="chip">Owner reviewed</span></div>
        <table className="table">
          <thead><tr><th>Type</th><th>Target</th><th>Status</th><th>Reason</th><th>Actions</th></tr></thead>
          <tbody>
            {approvals.map((approval) => (
              <tr key={approval.id}>
                <td>{approval.approval_type}</td>
                <td>{approval.target_type} #{approval.target_id}</td>
                <td><span className={approval.status === "APPROVED" ? "badge good" : approval.status === "REJECTED" ? "badge bad" : "badge warn"}>{approval.status}</span></td>
                <td className="small">{approval.reason}</td>
                <td>
                  {approval.status === "PENDING" ? (
                    <div className="actions">
                      <form action={approveAction}><input type="hidden" name="id" value={approval.id} /><button className="button">Approve</button></form>
                      <form action={rejectAction}><input type="hidden" name="id" value={approval.id} /><button className="button secondary">Reject</button></form>
                    </div>
                  ) : <span className="small">Done</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
