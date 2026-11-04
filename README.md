# 🖨️ Prusa i3 MK3S Klipper & Raspberry Pi 4 Homelab

Configuration repository for **Prusa i3 MK3S (Bear 2.1 Frame + Bondtech BMG + E3D V6)** running **Klipper + Moonraker + Mainsail** and the **24/7 Raspberry Pi 4 Homelab Stack** (Tailscale Mesh VPN, Pi-hole DNS, Uptime Kuma monitoring, Portainer).

---

## 🛠️ Hardware Setup

- **Printer**: Original Prusa i3 MK3S with Bear 2.1 Full Extrusion Frame
- **Extruder**: Bondtech BMG Extruder with E3D V6 All-Metal Hotend
- **Controller Board**: Ultimachine Einsy RAMBo 1.1a (ATmega2560 @ 16MHz, UART0)
- **Host SBC**: Raspberry Pi 4 Model B (4GB RAM) running Raspberry Pi OS (64-bit)
- **Firmware / UI**: Klipper Firmware + Moonraker API + Mainsail Web Interface + Mobileraker & OctoApp Companion

---

## 📁 Repository Structure

```text
├── klipper/
│   ├── printer.cfg          # Live primary Klipper hardware configuration
│   ├── moonraker.conf       # Moonraker API server configuration & update manager
│   ├── mainsail.cfg         # Mainsail macro library and client variables
│   ├── mobileraker.conf     # Mobile notifications and telemetry push
│   ├── octoapp.conf         # OctoApp plugin configuration
│   ├── KAMP_Settings.cfg    # Klipper Adaptive Meshing & Purging settings
│   └── history/             # Tuning archives and previous revision backups
│       ├── printer.cfg.current
│       ├── printer.cfg.fixed
│       ├── printer.cfg.working_clean
│       └── ...
├── homelab/
│   ├── docker-compose.yml   # Multi-service stack (Tailscale, Pi-hole, Uptime Kuma, Portainer)
│   ├── setup.sh             # 1-Click setup script for Raspberry Pi OS
│   └── README.md            # Homelab installation and port forwarding guide
├── gcode/                   # Pre-sliced repair components library (PETG/PLA)
│   ├── bose_qc_slider.gcode
│   ├── joycon_rail_latch.gcode
│   ├── t480_nvme_caddy.gcode
│   ├── xbox_battery_cover.gcode
│   └── xm4_hinge_swivel.gcode
└── tools/
    └── prusalink_bridge.py  # Local PrusaLink / Moonraker status bridge
```

---

## 🚀 Homelab Docker Stack

The Raspberry Pi 4 hosts essential local infrastructure using Docker:

| Service | Port | Description |
|---|---|---|
| **Tailscale** | Mesh VPN | Zero-config remote access from any phone or laptop |
| **Pi-hole** | `53`, `8088` | Network-wide ad & tracker blocking DNS sinkhole |
| **Uptime Kuma** | `3001` | Service monitoring & latency alerts |
| **Portainer** | `9000` | Web GUI for Docker container management |
| **Mainsail / Klipper** | `80` | Local 3D printer web dashboard |

To deploy or update the homelab services:
```bash
cd homelab
docker compose pull
docker compose up -d
```

---

## 🔧 Syncing Klipper Configs to Pi

To upload changes from this repository to the active printer on the Pi:
```bash
scp klipper/printer.cfg pi@100.126.201.29:/home/pi/printer_data/config/printer.cfg
ssh pi@100.126.201.29 "systemctl restart klipper"
```
Or use the Mainsail Web Interface configuration editor.
