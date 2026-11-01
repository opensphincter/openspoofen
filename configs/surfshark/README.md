Place downloaded Surfshark manual OpenVPN `.ovpn` profiles in this directory.

The current adapter scans filenames in this folder to build the available location list shown in the UI.

Recommended workflow:

1. Download the manual OpenVPN profiles from Surfshark.
2. Copy the `.ovpn` files into this directory.
3. Install `openvpn` on the Raspberry Pi image.
4. Enter the manual service username and password through the UI.

Do not commit real credentials or modified profile files containing secrets.