# OpenSpoofen documentation

Start with the [README](../README.md) for what OpenSpoofen is and a quickstart. These pages go deeper.

## Guides

Step-by-step pages for setting up and running the appliance.

- [Windows laptop to Raspberry Pi deployment](guides/windows-laptop-deployment.md): load a Pi from a Windows laptop.
- [Current hardware TV test](guides/current-hardware-tv-test.md): bench wiring for Wi-Fi or USB-Ethernet upstream and Ethernet to the TV.
- [LAN deployment patterns](guides/lan-deployment-patterns.md): where the Pi sits on a home network and how clients reach it.
- [Provider account integration](guides/provider-account-integration.md): connect NordVPN, Mullvad, ExpressVPN, Proton VPN or Surfshark.
- [Testing and simulation](guides/testing-and-simulation.md): the mock provider, the Linux namespace lab and image-build testing.

## Design

Why the appliance is built the way it is.

- [Research and architecture](design/research-and-architecture.md): findings and the recommended technical design.
- [First boot and image strategy](design/first-boot-and-image-strategy.md): first-boot flow, credentials and the image pipeline.
- [Hardware I/O and form factor](design/hardware-io-and-form-factor.md): Pi I/O, topologies and enclosure options.

## Reference

- [VPN provider comparison](reference/vpn-provider-comparison.md): appliance fit and adapter support per provider.
- [Provider programmatic access](reference/provider-programmatic-access.md): tokens, credentials and config exports each provider offers.
- [Configuration](../configs/openspoofen.env.example): every `RP_` setting, with defaults.
- [Pi 3 case](../designs/pi3-case/README.md): a printable enclosure.

## External

- [Installing the NordVPN app on Linux](https://support.nordvpn.com/hc/en-us/articles/20196094470929-How-to-install-the-NordVPN-app-on-Linux-distributions) (NordVPN support).
