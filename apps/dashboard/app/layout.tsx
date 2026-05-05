import "./globals.css";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Agency Operator",
  description: "Logged agency automation dashboard",
};

const links = [
  { label: "Overview", href: "/", icon: "OV", count: "01" },
  { label: "Leads", href: "/leads", icon: "LD", count: "02" },
  { label: "Approvals", href: "/approvals", icon: "AP", count: "03" },
  { label: "Sites", href: "/sites", icon: "ST", count: "04" },
  { label: "Payments", href: "/payments", icon: "PY", count: "05" },
  { label: "Actions", href: "/actions", icon: "LG", count: "06" },
];

const rail = ["AO", "AI", "RG", "EM", "KV", "VC"];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <aside className="rail" aria-label="Operator rail">
            <div className="rail-logo" />
            <div className="rail-icons">
              {rail.map((item, index) => (
                <div className={index === 0 ? "rail-dot active" : "rail-dot"} key={item}>{item}</div>
              ))}
            </div>
            <div className="rail-footer">
              <div className="rail-dot">EU</div>
              <div className="rail-dot">24</div>
            </div>
          </aside>

          <aside className="sidebar">
            <div className="brand-lockup">
              <div className="brand-mark" />
              <div>
                <div className="brand">Agency Operator</div>
                <div className="tagline">European web agency control room</div>
              </div>
            </div>

            <div className="nav-label">Main systems</div>
            <nav className="nav" aria-label="Main navigation">
              {links.map((link) => (
                <Link key={link.href} href={link.href}>
                  <span className="nav-icon">{link.icon}</span>
                  <span>{link.label}</span>
                  <span className="nav-count">{link.count}</span>
                </Link>
              ))}
            </nav>

            <div className="nav-label">Revenue target</div>
            <div className="operator-card">
              <div className="metric">Month one</div>
              <strong>10 x 1k</strong>
              <div className="small">Kiwify checkout, Vercel deploys, NVIDIA assisted previews.</div>
            </div>
          </aside>

          <main className="main">
            <div className="mobile-header">
              <div className="mobile-brand">
                <div className="brand-lockup" style={{ marginBottom: 0 }}>
                  <div className="brand-mark" />
                  <div>
                    <div className="brand">Agency Operator</div>
                    <div className="tagline">EU control room</div>
                  </div>
                </div>
                <span className="chip green">Live</span>
              </div>
              <nav className="mobile-nav" aria-label="Mobile navigation">
                {links.map((link) => <Link key={link.href} href={link.href}>{link.label}</Link>)}
              </nav>
            </div>
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
