import "./globals.css";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Agency Operator",
  description: "Logged agency automation dashboard",
};

const links = [
  ["Overview", "/"],
  ["Leads", "/leads"],
  ["Approvals", "/approvals"],
  ["Sites", "/sites"],
  ["Payments", "/payments"],
  ["Actions", "/actions"],
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <aside className="sidebar">
            <div className="brand">Agency Operator</div>
            <div className="tagline">Revenue machine MVP with logs, gates, and transparent outreach.</div>
            <nav className="nav">
              {links.map(([label, href]) => (
                <Link key={href} href={href}>{label}</Link>
              ))}
            </nav>
          </aside>
          <main className="main">{children}</main>
        </div>
      </body>
    </html>
  );
}
