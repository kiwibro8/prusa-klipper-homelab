# Prusa MK3S Klipper Config & Pi 4 Homelab

Configuration files for a Prusa i3 MK3S running Klipper, plus a small Docker-based homelab stack hosted on the same Raspberry Pi 4.

## Hardware Setup

- **Printer**: Prusa i3 MK3S with a Bear 2.1 aluminum extrusion frame
- **Extruder / Hotend**: Bondtech BMG geared extruder (3:1) with an E3D V6 all-metal hotend
- **Probe**: SuperPINDA
- **Mainboard**: Ultimachine Einsy RAMBo 1.1a (ATmega2560, TMC2130 drivers on SPI, sensorless homing on X/Y)
- **Host SBC**: Raspberry Pi 4 Model B (4GB), connected to the Einsy board over UART (`/dev/ttyAMA0`)

## Software Stack

- **Klipper**: Core printer firmware
- **Moonraker**: Web API and update manager
- **Mainsail**: Primary web interface
- **KAMP**: Klipper Adaptive Meshing and Purging for faster print starts
- **Mobileraker & OctoApp**: Mobile push notifications and status tracking

## Repository Layout

```text
├── klipper/
│   ├── printer.cfg          # Active Klipper configuration
│   ├── mainsail.cfg         # Mainsail macros and pause/resume logic
│   ├── moonraker.conf       # Moonraker configuration and update channels
│   ├── KAMP_Settings.cfg    # Adaptive bed mesh & purge parameters
│   ├── mobileraker.conf     # Mobile notifications config
│   ├── octoapp.conf         # OctoApp plugin config
│   └── history/             # Calibration archives and backup configs
└── homelab/
    ├── docker-compose.yml   # Pi-hole, Tailscale, Uptime Kuma, Portainer
    ├── setup.sh             # Initial setup script for the Pi
    └── README.md            # Service details and port map
```

## Homelab Services

The Pi 4 runs a few lightweight home network utilities in Docker containers alongside Klipper:

- **Pi-hole**: Network-wide DNS ad-blocking (`53`, web UI on `8088`)
- **Tailscale**: Private mesh VPN for remote access outside the local network
- **Uptime Kuma**: Self-hosted uptime monitoring (`3001`)
- **Portainer**: Web UI for inspecting containers (`9000`)

To start or update the services:

```bash
cd homelab
docker compose pull
docker compose up -d
```

## Deploying Config Updates

Changes to `printer.cfg` can be edited directly through the Mainsail web interface, or copied over SSH:

```bash
scp klipper/printer.cfg pi@<PI_IP>:/home/pi/printer_data/config/printer.cfg
ssh pi@<PI_IP> "systemctl restart klipper"
```
