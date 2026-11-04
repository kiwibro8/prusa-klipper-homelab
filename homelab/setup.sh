#!/bin/bash
set -e

# Setup script for Raspberry Pi 4 docker stack
# Services: Pi-hole, Tailscale, Uptime Kuma, Portainer

echo "==> Updating package indices..."
sudo apt update && sudo apt upgrade -y

echo "==> Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker "$USER"
    rm get-docker.sh
    echo "Docker installed."
else
    echo "Docker is already installed."
fi

sudo apt install -y docker-compose-plugin

echo "==> Creating persistent data directories..."
mkdir -p data/pihole data/dnsmasq.d data/tailscale data/uptime-kuma data/portainer

# Free port 53 from systemd-resolved stub listener if needed
if sudo lsof -i :53 | grep -q systemd-resolve; then
    echo "==> Disabling systemd-resolved DNS stub listener on port 53..."
    sudo sed -r -i.orig 's/#?DNSStubListener=yes/DNSStubListener=no/g' /etc/systemd/resolved.conf
    sudo systemctl restart systemd-resolved
fi

echo "==> Starting containers..."
sudo docker compose up -d

echo ""
echo "Setup complete. Local endpoints:"
echo "- Pi-hole:     http://$(hostname -I | cut -d' ' -f1):8088/admin"
echo "- Portainer:    http://$(hostname -I | cut -d' ' -f1):9000"
echo "- Uptime Kuma:  http://$(hostname -I | cut -d' ' -f1):3001"
echo ""
echo "To authenticate Tailscale, run:"
echo "  sudo docker exec -it tailscale tailscale up"
