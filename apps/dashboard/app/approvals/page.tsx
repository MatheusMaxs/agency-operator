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
  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <h1>Approvals</h1>
          <div className="sub">Manual gates before sensitive actions like first outreach.</div>
        </div>
      </div>
      <div className="card">
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
