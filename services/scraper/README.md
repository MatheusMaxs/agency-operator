# Scraper Service

MVP scraping is routed through `services/api/app/tools.py::discover_businesses`. It can now import structured public business rows from Hermes/browser-use as well as demo/manual seed data.

Future implementation should use browser-use + Playwright with strict rate limits, source URL storage, dedupe, and robots/legal checks.
