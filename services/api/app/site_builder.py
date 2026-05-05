from html import escape


def build_site(business: dict, preview_url: str | None = None) -> tuple[str, str, dict]:
    name = escape(business.get("name") or "Local Business")
    category = escape(business.get("category") or "local service")
    city = escape(business.get("city") or "your city")
    country = escape(business.get("country") or "Europe")
    phone = escape(business.get("phone") or "")
    email = escape(business.get("email") or "")

    brief = {
        "visual_direction": "warm editorial local-business landing page",
        "palette": ["#18241f", "#f6efe3", "#c98552", "#ffffff"],
        "sections": ["hero", "about", "services", "proof", "location", "faq", "contact"],
        "rules": ["no fake testimonials", "mobile first", "clear CTA", "localized copy"],
    }

    css = """
    :root { color-scheme: light; --ink:#18241f; --paper:#f6efe3; --accent:#c98552; --muted:#65746d; }
    * { box-sizing: border-box; }
    body { margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; color:var(--ink); background:var(--paper); }
    a { color: inherit; }
    .wrap { width:min(1120px, calc(100% - 32px)); margin:0 auto; }
    header { padding:24px 0; display:flex; justify-content:space-between; gap:18px; align-items:center; }
    .brand { font-weight:800; letter-spacing:-0.04em; font-size:22px; }
    .pill { border:1px solid rgba(24,36,31,.18); border-radius:999px; padding:10px 16px; text-decoration:none; }
    .hero { padding:56px 0 72px; display:grid; grid-template-columns: 1.15fr .85fr; gap:36px; align-items:center; }
    h1 { font-size: clamp(44px, 8vw, 92px); line-height:.9; letter-spacing:-.075em; margin:0 0 24px; }
    .lead { font-size: clamp(18px, 2vw, 23px); line-height:1.45; color:var(--muted); max-width:720px; }
    .cta { display:flex; flex-wrap:wrap; gap:12px; margin-top:30px; }
    .button { background:var(--ink); color:var(--paper); border-radius:16px; padding:15px 20px; text-decoration:none; font-weight:800; }
    .button.secondary { background:transparent; color:var(--ink); border:1px solid rgba(24,36,31,.2); }
    .card { background:#fffaf2; border:1px solid rgba(24,36,31,.12); border-radius:32px; padding:26px; box-shadow: 0 22px 70px rgba(24,36,31,.10); }
    .visual { min-height:420px; background: radial-gradient(circle at 35% 30%, #f0c39c, transparent 28%), linear-gradient(135deg, #22382f, #794f34); color:white; display:flex; align-items:end; }
    .visual strong { font-size:38px; line-height:1; letter-spacing:-.04em; }
    section { padding:64px 0; }
    .grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:18px; }
    h2 { font-size: clamp(32px, 4vw, 56px); line-height:1; letter-spacing:-.055em; margin:0 0 22px; }
    .service { padding:24px; border-radius:24px; background:rgba(255,255,255,.55); border:1px solid rgba(24,36,31,.10); }
    .service h3 { margin:0 0 8px; font-size:20px; }
    .muted { color:var(--muted); line-height:1.6; }
    footer { padding:36px 0; border-top:1px solid rgba(24,36,31,.12); color:var(--muted); }
    @media (max-width: 820px) { .hero, .grid { grid-template-columns:1fr; } .visual { min-height:300px; } header { align-items:flex-start; flex-direction:column; } }
    """

    html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{name} | {category} in {city}</title>
        <meta name="description" content="A modern website concept for {name}, a {category} in {city}, {country}." />
        <style>{css}</style>
      </head>
      <body>
        <div class="wrap">
          <header>
            <div class="brand">{name}</div>
            <a class="pill" href="#contact">Contact</a>
          </header>
          <main>
            <section class="hero">
              <div>
                <h1>A clearer online home for {name}.</h1>
                <p class="lead">A simple, fast, mobile-ready website concept for a {category} serving customers in {city}. Built to make the business easier to trust, find, and contact.</p>
                <div class="cta">
                  <a class="button" href="#contact">Request a booking</a>
                  <a class="button secondary" href="#services">See services</a>
                </div>
              </div>
              <div class="card visual"><strong>{city}<br />{category}</strong></div>
            </section>
            <section id="services">
              <h2>What customers need to know, fast.</h2>
              <div class="grid">
                <div class="service"><h3>Clear offer</h3><p class="muted">Explain the core service without making visitors search through social posts or old pages.</p></div>
                <div class="service"><h3>Mobile first</h3><p class="muted">Most local customers browse on a phone. This layout keeps actions visible and simple.</p></div>
                <div class="service"><h3>Contact ready</h3><p class="muted">Phone, email, address, and call-to-action are easy to find from every device.</p></div>
              </div>
            </section>
            <section>
              <div class="card">
                <h2>About {name}</h2>
                <p class="muted">This is a preview concept using public business information. Final copy, photos, menu/services, and legal details should be approved by the business owner before publication.</p>
              </div>
            </section>
            <section id="contact">
              <h2>Ready for real customers.</h2>
              <p class="muted">{phone if phone else "Phone can be added here."} {email if email else "Email can be added here."}</p>
              <div class="cta"><a class="button" href="mailto:{email}">Email {name}</a></div>
            </section>
          </main>
          <footer>Preview concept. No fake reviews, no copied design, no final publication before owner approval.</footer>
        </div>
      </body>
    </html>
    """
    return html, css, brief
