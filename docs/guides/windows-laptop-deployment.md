# Windows Laptop To Raspberry Pi Deployment

## Goal

Make the normal operator path simple:

1. Prepare the microSD card from the Windows laptop.
2. Boot the Raspberry Pi with headless access already enabled.
3. Run one PowerShell deploy command from the laptop.
4. Open the LAN UI from a phone or the laptop browser.

This is the supported easy path for the current repo.

## What "plug into the laptop" means in practice

For Raspberry Pi 4 and Raspberry Pi 5, the reliable operator path is:

- use the laptop to write the microSD card with Raspberry Pi Imager
- power the Pi normally with its own USB-C power supply
- connect the Pi to the same LAN as the laptop, or directly by Ethernet if the laptop can share internet access
- deploy the repo over SSH from the laptop

Direct single-cable USB provisioning is not the target path here. Pi 4 and Pi 5 are not a clean "USB gadget appliance" fit for this product, and building around that would make provisioning more fragile than it needs to be.

## Required laptop-side tools

- Windows laptop with PowerShell and OpenSSH client available
- Raspberry Pi Imager for Windows
- microSD card reader, built-in or USB
- this repository checked out on the laptop

## Required hardware for the Pi install path

- Raspberry Pi 4 or Raspberry Pi 5
- quality power supply matched to the model
- microSD card: 16 GB minimum for Raspberry Pi OS Lite, 32 GB recommended
- Ethernet cable if you want direct wired downstream to a TV or direct laptop-to-Pi setup

## Recommended operator workflow

### Step 1: Flash Raspberry Pi OS Lite with Imager

Use Raspberry Pi Imager on Windows and select:

- device: your Pi model
- OS: Raspberry Pi OS Lite 64-bit
- storage: the target microSD card

In Imager customisation, set:

- hostname, for example `openspoofen`
- admin username and password
- Wi-Fi credentials and the correct local Wi-Fi country code if Wi-Fi will be the upstream link
- SSH enabled
- optional Raspberry Pi Connect for fallback recovery

Use the actual regulatory country where the Pi will operate. Open-source users should not assume a U.S. default.

This matches Raspberry Pi's supported headless setup flow and removes the need for a monitor and keyboard.

### Step 2: Boot the Pi

- insert the imaged microSD card into the Pi
- connect upstream networking
- connect power
- wait for the Pi to appear on the network

Typical host targets:

- `openspoofen.local`
- a DHCP-assigned IP address

### Step 3: Deploy the repo from Windows

From the repository root on the laptop:

```powershell
.\bootstrap\deploy-to-pi.ps1 -HostName openspoofen.local -UserName <pi-username>
```

If you already have a local appliance env file:

```powershell
.\bootstrap\deploy-to-pi.ps1 -HostName openspoofen.local -UserName <pi-username> -LocalEnvFile .\configs\openspoofen.env.example
```

If you want the initial deployment to also install the upstream and TV-LAN topology files, pass them in the same command:

```powershell
.\bootstrap\deploy-to-pi.ps1 \
	-HostName openspoofen.local \
	-UserName <pi-username> \
	-LocalEnvFile .\configs\openspoofen.env.example \
	-LocalWifiEnvFile .\configs\wifi-uplink.env.example \
	-LocalTvModeEnvFile .\configs\tv-ethernet-mode.env.example
```

Recommended operator path:

- copy each example env file into a local, untracked variant
- set the real hostname, provider, password/token references, Wi-Fi country, and interface names there
- use `eth0` for the TV-facing port on older single-Ethernet boards
- use `eth1` or `enx...` as `RP_TV_UPLINK_IFACE` when the upstream is a USB Ethernet adapter

What the script does:

- packages the repo from the laptop while skipping local junk and secrets
- uploads it to the Pi over `scp`
- runs `bootstrap/install.sh` remotely over `ssh`
- installs dependencies and the systemd service on the Pi
- optionally installs the env file to `/etc/openspoofen/openspoofen.env`
- optionally installs the Wi-Fi uplink env file to `/etc/openspoofen/secrets/wifi-uplink.local.env`
- optionally installs the TV-LAN env file to `/etc/openspoofen/tv-ethernet-mode.env`

### Step 4: Open the LAN UI

After deployment:

- browse to `http://openspoofen.local:8080`
- complete the first-boot setup screen
- sign in with the admin password
- switch regions from the dashboard

If you want stricter first-time browser pairing, set `RP_REQUIRE_PAIRING_TOKEN=true` in the main env file before deployment.

## Direct laptop-to-Pi connection notes

If you want to plug the Pi directly into the laptop instead of using the home router:

- the laptop needs a physical Ethernet port or a USB-to-Ethernet adapter
- the Pi still needs its own power supply
- the laptop must provide internet sharing if the Pi is going to install packages or use upstream Wi-Fi through the laptop path

This mode is useful for first deployment and bench testing, but it should not be treated as the primary appliance topology.

## What still needs real hardware validation

- USB Ethernet adapter choice for all-wired Pi mode
- downstream DHCP and DNS behavior with a real TV
- first-deploy experience with both optional topology env files provided from Windows
- fail-closed routing behavior when the VPN drops
- WireGuard profile switching against real providers on Pi hardware