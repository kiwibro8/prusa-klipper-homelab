# Raspberry Pi 4 Security, Privacy & VPN Homelab Stack

Acest pachet instaleaz? ?i configureaz? automat:
1. **Pi-hole (DNS AdBlocker)**: Blocheaz? reclamele ?i trackerii pe tot routerul/re?eaua de acas?.
2. **Tailscale (Mesh VPN Privat)**: ??i ofer? acces criptat de oriunde la Raspberry Pi, la Prusa ?i la scraperul OLX, f?r? port-forwarding.
3. **Uptime Kuma**: Monitorizeaz? disponibilitatea serviciilor (PrusaLink, OLX Bot, Internet).
4. **Portainer**: Interfa?? web grafic? pentru Docker.

### Cum ?l rulezi c?nd ??i sose?te Raspberry Pi 4:
```bash
# 1. Copiaz? folderul pe Pi sau cloneaz?-l
cd deploy/pi4_homelab

# 2. F? scriptul executabil ?i ruleaz?-l
chmod +x setup.sh
./setup.sh
```
