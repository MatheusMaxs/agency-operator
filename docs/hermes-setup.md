# Hermes Setup

Hermes should call the MCP bridge, not edit the database directly.

Install Hermes separately according to the upstream project instructions. Then configure a local HTTP tool server pointing at:

```text
http://127.0.0.1:8100
```

Useful endpoints:

- `GET /manifest`
- `POST /call`
- `POST /jsonrpc`

Recommended allowed commands:

- `curl http://127.0.0.1:8100/manifest`
- `curl -X POST http://127.0.0.1:8100/call ...`

Recommended forbidden commands:

- Direct database mutation commands.
- Bulk email scripts outside the API.
- Browser-auth ChatGPT/Codex automation for production.
- Any destructive file or server commands.

Start with manual scheduling. Add cron only after the first safe end-to-end campaign works.

For month one, Hermes should use browser-use/Playwright to collect public business data, then import structured rows through `discover_businesses` instead of writing directly to Postgres.
