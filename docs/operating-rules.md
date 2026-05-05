# Operating Rules

System objective: find local European businesses with weak digital presence, create legal simple website previews, contact them transparently, and optimize toward paid customers.

Hard rules:

- Log every tool call in `agent_actions`.
- Do not contact businesses marked `DO_NOT_CONTACT`.
- Do not send duplicate first outreach.
- Do not pretend to be human.
- Do not clone protected designs exactly.
- Do not use copyrighted images unless licensed.
- Do not publish final client site before payment and owner approval.
- Do not exceed daily email limits.
- Keep manual approval for outreach until conversion and complaint data is known.
- Escalate legal, payment, contract, refund, or angry-customer issues to the owner.

MVP states:

- `DISCOVERED`
- `ENRICHED`
- `HAS_NO_SITE`
- `HAS_BAD_SITE`
- `QUALIFIED`
- `SITE_GENERATED`
- `SITE_DEPLOYED`
- `CONTACT_READY`
- `CONTACTED`
- `REPLIED`
- `INTERESTED`
- `PAYMENT_LINK_SENT`
- `PAID`
- `DELIVERED`
- `REJECTED`
- `DO_NOT_CONTACT`
- `FAILED`

Approval gates:

- Auto scrape: allowed for low-volume legal sources.
- Auto audit: allowed.
- Auto score: allowed.
- Auto generate site preview: allowed.
- Auto deploy preview: allowed.
- First email outreach: manual approval at first.
- Auto reply: disabled until confidence and templates are proven.
- Payment link: allowed only after clear customer interest.

First-month commercial targets:

- Primary offer: complete local business website for `1000 EUR`.
- Care plans: `49-149 EUR/month` for hosting, updates, and analytics.
- Payment provider: Kiwify for month one, with alternative processors reviewed after validation.

Daily review questions:

- How many leads were discovered?
- How many were qualified?
- How many previews were generated?
- How many emails were approved/sent?
- How many replies and complaints?
- What was total cost?
- What changed conversion?
