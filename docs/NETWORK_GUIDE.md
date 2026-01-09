# Network Configuration Guide

Complete guide for network setup, connection management, and troubleshooting.

## Table of Contents

1. [Network Architecture](#network-architecture)
2. [Connection Methods](#connection-methods)
3. [Static IP Configuration](#static-ip-configuration)
4. [WiFi Setup](#wifi-setup)
5. [Firewall Configuration](#firewall-configuration)
6. [Network Troubleshooting](#network-troubleshooting)

## Network Architecture

### System Overview

```
┌─────────────────┐                    ┌──────────────────┐
│   PC Application│                    │  Raspberry Pi    │
│   (Qt GUI)      │◄──── WebSocket ───►│  (Robot Server)  │
│                 │    Port 8888       │                  │
│  - Control UI   │                    │  - Motor Control │
│  - Video Stream │                    │  - Camera Stream │
│  - AI Chat      │                    │  - Sensors       │
│  - SLAM View    │                    │  - LiDAR         │
└─────────────────┘                    └──────────────────┘
         │                                      │
         └──────── Local Network (WiFi/Ethernet)
```

### Communication Protocol

- **Primary Connection:** WebSocket (TCP)
- **Default Port:** 8888
- **Protocol:** JSON over WebSocket
- **Encoding:** UTF-8
- **Video Stream:** MJPEG over WebSocket or separate HTTP stream

### Network Requirements

- **Bandwidth:** 5 Mbps minimum, 10+ Mbps recommended
- **Latency:** < 50ms for responsive control
- **Connection:** Same local network (LAN/WLAN)

## Connection Methods

### Method 1: Direct WiFi Connection (Recommended)

Both Pi and PC connect to same WiFi network.

**Advantages:**
- Simple setup
- Works anywhere with WiFi
- No cables needed

**Setup:**
1. Connect Pi to WiFi (during OS setup or later)
2. Connect PC to same WiFi
3. Pi auto-detects and displays IP
4. Enter IP in PC app

### Method 2: Ethernet Connection

Connect Pi and PC via Ethernet cable or switch.

**Advantages:**
- Lower latency
- More stable connection
- Higher bandwidth

**Setup:**
1. Connect Pi to router via Ethernet
2. Connect PC to same router
3. Or use direct Ethernet cable (requires static IP)

### Method 3: Pi as Access Point (Advanced)

Pi creates its own WiFi network.

**Advantages:**
- Works without existing WiFi
- Portable - works anywhere
- Full control over network

**Setup:** See [Pi Access Point Configuration](#pi-access-point-configuration)

### Method 4: Direct Ethernet (Ad-Hoc)

Direct cable between Pi and PC.

**Advantages:**
- No router needed
- Maximum speed
- Completely isolated

**Disadvantages:**
- Requires static IP configuration
- No internet access

**Setup:** See [Direct Ethernet Configuration](#direct-ethernet-configuration)

## Static IP Configuration

### Why Use Static IP?

- IP address doesn't change after reboot
- Easier connection from PC
- Can configure connection profiles
- Better for production robots

### Configure Static IP on Raspberry Pi

#### Method 1: Using dhcpcd (Raspberry Pi OS)

```bash
sudo nano /etc/dhcpcd.conf
```

Add at end of file:

```bash
# Static IP configuration
interface wlan0  # Use 'eth0' for Ethernet
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Restart networking:
```bash
sudo systemctl restart dhcpcd
```

#### Method 2: Using NetworkManager

```bash
# List connections
nmcli connection show

# Modify connection
sudo nmcli connection modify "Wired connection 1" \
  ipv4.addresses 192.168.1.100/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns "8.8.8.8,8.8.4.4" \
  ipv4.method manual

# Restart connection
sudo nmcli connection down "Wired connection 1"
sudo nmcli connection up "Wired connection 1"
```

#### Method 3: Router DHCP Reservation

1. Find Pi's MAC address:
   ```bash
   ip link show
   # or
   ifconfig
   ```

2. Log into your router (usually 192.168.1.1)
3. Find DHCP settings
4. Add MAC address → IP address reservation
5. Reboot Pi

### Verify Static IP

```bash
# Check IP address
ip addr show

# Test connectivity
ping 192.168.1.1  # Gateway
ping 8.8.8.8      # Internet
```

## WiFi Setup

### Configure WiFi on Raspberry Pi

#### During OS Installation

1. In Raspberry Pi Imager:
   - Click settings gear ⚙️
   - Enter WiFi SSID and password
   - Flash SD card

#### After Installation

**Method 1: Using raspi-config**

```bash
sudo raspi-config
# Navigate to: System Options → Wireless LAN
# Enter SSID and password
```

**Method 2: Manual Configuration**

```bash
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

Add:
```
network={
    ssid="YourWiFiName"
    psk="YourPassword"
    key_mgmt=WPA-PSK
}
```

Restart:
```bash
sudo systemctl restart wpa_supplicant
```

**Method 3: Using nmcli**

```bash
# Scan for networks
sudo nmcli device wifi list

# Connect to network
sudo nmcli device wifi connect "YourWiFiName" password "YourPassword"
```

### Multiple WiFi Networks

```bash
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

```
# Priority: Higher number = higher priority
network={
    ssid="Home_WiFi"
    psk="HomePassword"
    priority=1
}

network={
    ssid="Workshop_WiFi"
    psk="WorkshopPassword"
    priority=2
}

network={
    ssid="Mobile_Hotspot"
    psk="HotspotPassword"
    priority=3
}
```

### WiFi Power Management

Disable WiFi power saving for better performance:

```bash
sudo nano /etc/rc.local
```

Add before `exit 0`:
```bash
# Disable WiFi power management
iwconfig wlan0 power off
```

## Pi Access Point Configuration

Turn Pi into WiFi hotspot.

### Install Required Packages

```bash
sudo apt update
sudo apt install -y hostapd dnsmasq
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq
```

### Configure Static IP for AP

```bash
sudo nano /etc/dhcpcd.conf
```

Add:
```
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
```

### Configure DHCP Server

```bash
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo nano /etc/dnsmasq.conf
```

Add:
```
interface=wlan0
dhcp-range=192.168.4.10,192.168.4.50,255.255.255.0,24h
```

### Configure Access Point

```bash
sudo nano /etc/hostapd/hostapd.conf
```

Add:
```
interface=wlan0
driver=nl80211
ssid=RobotController
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=robot12345
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```

### Enable Services

```bash
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
sudo reboot
```

### Connect PC to Pi AP

1. Look for WiFi network: `RobotController`
2. Password: `robot12345`
3. Pi IP will be: `192.168.4.1`
4. Enter in PC app: `192.168.4.1:8888`

## Direct Ethernet Configuration

Connect PC and Pi with Ethernet cable (no router).

### Configure Pi

```bash
sudo nano /etc/dhcpcd.conf
```

Add:
```
interface eth0
static ip_address=192.168.2.2/24
```

### Configure PC

**Windows:**
1. Control Panel → Network and Sharing Center
2. Change adapter settings
3. Right-click Ethernet → Properties
4. IPv4 Properties
5. Use following IP:
   - IP: `192.168.2.1`
   - Subnet: `255.255.255.0`

**Linux:**
```bash
sudo nmcli connection modify "Wired connection 1" \
  ipv4.addresses 192.168.2.1/24 \
  ipv4.method manual
```

**macOS:**
1. System Preferences → Network
2. Select Ethernet
3. Configure IPv4: Manually
4. IP: `192.168.2.1`
5. Subnet: `255.255.255.0`

### Test Connection

From PC:
```bash
ping 192.168.2.2
```

Connect using: `192.168.2.2:8888`

## Firewall Configuration

### Raspberry Pi Firewall

#### Check if UFW is installed

```bash
sudo apt install ufw
```

#### Configure Firewall

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow robot server port
sudo ufw allow 8888/tcp

# Allow camera stream (if separate)
sudo ufw allow 8889/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

#### Allow Specific IP Only

```bash
# Allow only your PC
sudo ufw allow from 192.168.1.50 to any port 8888
```

### PC Firewall

**Windows:**
1. Windows Security → Firewall & network protection
2. Advanced settings
3. Inbound Rules → New Rule
4. Port → TCP → 8888
5. Allow connection

**Linux (UFW):**
```bash
sudo ufw allow 8888/tcp
```

**macOS:**
- Usually allows outgoing connections by default

## Network Troubleshooting

### Can't Find Pi IP Address

**Solution 1: Check on Pi directly**
```bash
hostname -I
# or
ip addr show
```

**Solution 2: Scan network from PC**
```bash
# Linux/Mac
sudo nmap -sn 192.168.1.0/24

# Windows (use Advanced IP Scanner)
# Download from: https://www.advanced-ip-scanner.com/
```

**Solution 3: Check router**
- Log into router web interface (192.168.1.1)
- Look for "Connected Devices" or "DHCP Clients"
- Find device named "robot-pi" or "raspberrypi"

### Connection Refused

**Check if server is running:**
```bash
# On Pi
sudo netstat -tulpn | grep 8888
# or
sudo ss -tulpn | grep 8888
```

**Start server:**
```bash
cd ~/qt-robot-controller/pi_server
python3 server.py
```

**Check firewall:**
```bash
sudo ufw status
sudo ufw allow 8888/tcp
```

### Connection Timeout

**Test basic connectivity:**
```bash
# From PC
ping 192.168.1.100  # Use your Pi IP
```

**Test port:**
```bash
# Linux/Mac
telnet 192.168.1.100 8888

# Windows
Test-NetConnection -ComputerName 192.168.1.100 -Port 8888
```

### Slow Connection / High Latency

**Check WiFi signal:**
```bash
# On Pi
iwconfig wlan0 | grep -i "signal level"
```

**Improve signal:**
- Move closer to router
- Use 5GHz WiFi if available
- Switch to Ethernet
- Reduce interference (microwave, other devices)

**Check network load:**
```bash
# Monitor bandwidth
iftop
# or
nload
```

### Multiple Devices on Network

**Change port if conflict:**
```bash
# On Pi
nano ~/qt-robot-controller/pi_server/config/hardware_config.yaml
```

Change:
```yaml
server_port: 8889  # Use different port
```

### DNS Resolution Issues

**Use IP address instead of hostname:**
- Instead of: `robot-pi.local:8888`
- Use: `192.168.1.100:8888`

**Install Avahi (for .local names):**
```bash
sudo apt install avahi-daemon
sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon
```

## Performance Optimization

### Reduce Video Latency

```yaml
# In hardware_config.yaml
camera:
  width: 320  # Lower resolution
  height: 240
  fps: 15     # Lower frame rate
  stream_quality: 60  # Lower quality
```

### Network Monitoring

```bash
# Install monitoring tools
sudo apt install iftop nethogs

# Monitor bandwidth by interface
sudo iftop -i wlan0

# Monitor bandwidth by process
sudo nethogs
```

### Connection Quality Test

```bash
# Continuous ping test
ping -c 100 192.168.1.100

# Check packet loss and latency
```

Good connection:
- Latency: < 10ms (LAN) or < 50ms (WiFi)
- Packet loss: 0%

## Advanced Topics

### VPN Setup

For remote control over internet (not recommended for real-time control).

### Port Forwarding

Expose robot to internet (security risk!).

### Multiple Robots

Assign different IPs and ports:
- Robot 1: `192.168.1.101:8888`
- Robot 2: `192.168.1.102:8888`
- Robot 3: `192.168.1.103:8888`

## Security Considerations

### Current Setup (Local Network)

- ✅ Safe for home/lab use
- ✅ No authentication needed on trusted network
- ✅ Fast communication

### For Production (Recommended)

- 🔒 Add authentication tokens
- 🔒 Use TLS/SSL encryption
- 🔒 Implement user accounts
- 🔒 Rate limiting
- 🔒 Firewall rules

### Never Do This

- ❌ Expose robot directly to internet without security
- ❌ Use default passwords
- ❌ Allow connections from unknown networks

## Summary

**Quick Setup:**
1. Connect Pi and PC to same WiFi
2. Note Pi IP address from terminal
3. Enter IP in PC app
4. Click Connect

**For Stable Connection:**
- Use static IP or DHCP reservation
- Use Ethernet if possible
- Disable WiFi power management

**For Portable Operation:**
- Configure Pi as access point
- Connect PC to Pi's WiFi
- Always use IP: `192.168.4.1`
