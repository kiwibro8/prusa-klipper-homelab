# Homelab Services

Docker stack running alongside Klipper on the Raspberry Pi 4.

## Services & Ports

- **Pi-hole**: DNS sinkhole on port `53`, web dashboard on port `8088` (`http://<pi-ip>:8088/admin`).
- **Tailscale**: Host networking VPN for secure remote access without port forwarding.
- **Uptime Kuma**: Monitoring dashboard on port `3001`.
- **Portainer**: Docker management UI on port `9000`.

## Quick Start

```bash
cd homelab
chmod +x setup.sh
./setup.sh
```

Or run compose directly:

```bash
cd homelab
docker compose up -d
```

To link Tailscale on initial start:

```bash
docker exec -it tailscale tailscale up
```
