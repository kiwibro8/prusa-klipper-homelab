#!/bin/bash
# ==============================================================================
# RASPBERRY PI 4 HOMELAB AUTOMATED SETUP
# Installs: Docker, Docker Compose, Pi-hole (AdBlock), Tailscale (VPN),
#           Uptime Kuma, and Portainer in under 3 minutes!
# ==============================================================================

set -e

echo "?? [1/5] Actualizare pachete de sistem..."
sudo apt update && sudo apt upgrade -y

echo "?? [2/5] Instalare Docker Engine & Docker Compose..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "? Docker instalat cu succes!"
else
    echo "? Docker este deja instalat."
fi

# Ensure docker compose plugin exists
sudo apt install -y docker-compose-plugin

echo "?? [3/5] Creare directoare de date persistente..."
mkdir -p data/pihole data/dnsmasq.d data/tailscale data/uptime-kuma data/portainer

# Disable systemd-resolved DNS stub listener on port 53 if active so Pi-hole can bind
if sudo lsof -i :53 | grep -q systemd-resolve; then
    echo "?? Eliberare port 53 de catre systemd-resolved..."
    sudo sed -r -i.orig 's/#?DNSStubListener=yes/DNSStubListener=no/g' /etc/systemd/resolved.conf
    sudo systemctl restart systemd-resolved
fi

echo "?? [4/5] Pornire containere Docker (Pi-hole, Tailscale, Kuma, Portainer)..."
sudo docker compose up -d

echo "?? [5/5] Conectare Tailscale VPN..."
echo "Ruleaza urmatoarea comanda pentru autentificare Tailscale:"
echo "?? sudo docker exec -it tailscale tailscale up"

echo ""
echo "=============================================================================="
echo "?? HOMELAB INSTALAT CU SUCCES PE RASPBERRY PI 4!"
echo "=============================================================================="
echo "?? Dashboard-uri disponibile in reteaua locala:"
echo "? Pi-hole (AdBlock):   http://$(hostname -I | cut -d' ' -f1):8088/admin"
echo "? Portainer (Docker):  http://$(hostname -I | cut -d' ' -f1):9000"
echo "? Uptime Kuma:         http://$(hostname -I | cut -d' ' -f1):3001"
echo "=============================================================================="
