# Infra

Docker Compose currently lives at the project root for simple MVP operation.

Recommended month-one VPS target: Hostinger KVM 4 or equivalent, with enough RAM for Docker, Redis/Postgres, Hermes, and browser automation workers.

Future production infra can move reverse proxy, Postgres tuning, Redis config, backups, and TLS files here.
