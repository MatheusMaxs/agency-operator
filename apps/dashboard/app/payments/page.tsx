import { apiGet } from "../../lib/api";

type Payment = {
  id: number;
  business_name: string;
  package_name: string;
  provider: string;
  payment_status: string;
  amount: number;
  currency: string;
  checkout_url: string | null;
  paid_at: string | null;
};

type Subscription = {
  id: number;
  business_name: string;
  plan_name: string;
  provider: string;
  status: string;
  amount: number;
  currency: string;
  checkout_url: string | null;
};

function money(amount: number, currency: string) {
  return `${currency.toUpperCase()} ${(amount / 100).toFixed(2)}`;
}

function badgeClass(status: string) {
  if (["PAID", "ACTIVE"].includes(status)) return "badge good";
  if (["FAILED", "CANCELED"].includes(status)) return "badge bad";
  return "badge warn";
}

export default async function PaymentsPage() {
  const [payments, subscriptions] = await Promise.all([
    apiGet<Payment[]>("/payments?limit=200"),
    apiGet<Subscription[]>("/subscriptions?limit=200"),
  ]);

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <h1>Payments</h1>
          <div className="sub">Kiwify upfront revenue and care-plan MRR.</div>
        </div>
      </div>
      <div className="card">
        <h2>Upfront</h2>
        <table className="table">
          <thead><tr><th>Business</th><th>Package</th><th>Status</th><th>Amount</th><th>Checkout</th></tr></thead>
          <tbody>
            {payments.map((payment) => (
              <tr key={payment.id}>
                <td>{payment.business_name}</td>
                <td>{payment.package_name}<div className="small">{payment.provider}</div></td>
                <td><span className={badgeClass(payment.payment_status)}>{payment.payment_status}</span></td>
                <td>{money(payment.amount, payment.currency)}</td>
                <td>{payment.checkout_url ? <a className="button secondary" href={payment.checkout_url} target="_blank" rel="noreferrer">Open</a> : <span className="small">none</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="card">
        <h2>Care Plans</h2>
        <table className="table">
          <thead><tr><th>Business</th><th>Plan</th><th>Status</th><th>Monthly</th><th>Checkout</th></tr></thead>
          <tbody>
            {subscriptions.map((subscription) => (
              <tr key={subscription.id}>
                <td>{subscription.business_name}</td>
                <td>{subscription.plan_name}<div className="small">{subscription.provider}</div></td>
                <td><span className={badgeClass(subscription.status)}>{subscription.status}</span></td>
                <td>{money(subscription.amount, subscription.currency)}</td>
                <td>{subscription.checkout_url ? <a className="button secondary" href={subscription.checkout_url} target="_blank" rel="noreferrer">Open</a> : <span className="small">none</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
