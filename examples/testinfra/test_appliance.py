"""Sample Testinfra checks for an OpenSpoofen appliance host.

Run against a Pi or Linux lab host with a command such as:
pytest -v examples/testinfra/test_appliance.py --hosts=ssh://pi@raspberrypi.local
"""


def test_web_service_unit_exists(host):
    service_file = host.file("/etc/systemd/system/openspoofen-web.service")
    assert service_file.exists


def test_python_runtime_is_available(host):
    python = host.file("/usr/bin/python3")
    assert python.exists
    assert python.mode & 0o111


def test_ip_forwarding_is_enabled(host):
    sysctl_value = host.sysctl("net.ipv4.ip_forward")
    assert sysctl_value == 1


def test_dnsmasq_is_installed(host):
    package = host.package("dnsmasq")
    assert package.is_installed