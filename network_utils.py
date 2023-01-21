import rp2
import network
import uasyncio
import settings



async def prepare_wifi(log=None):
    """
    Prepare Wi-Fi connection.

    https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf  # noqa
    """
    if not log:
        log = print
    # Set country code
    rp2.country(settings.COUNTRY)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    wlan.connect(settings.WIFI_SSID, settings.WIFI_PASSWORD)

    for i in range(10):
        status = wlan.status()
        if wlan.status() < 0 or wlan.status() >= network.STAT_GOT_IP:
            break
        log(f'Waiting ({i})... status={status}')
        await uasyncio.sleep(1)
    else:
        log('Wifi connection timed out.')
        raise RuntimeError('Wifi connection timed out.')

    # CYW43_LINK_DOWN (0)
    # CYW43_LINK_JOIN (1)
    # CYW43_LINK_NOIP (2)
    # CYW43_LINK_UP (3)
    # CYW43_LINK_FAIL (-1)
    # CYW43_LINK_NONET (-2)
    # CYW43_LINK_BADAUTH (-3)

    wlan_status = wlan.status()

    if wlan_status != network.STAT_GOT_IP:
        log('Wi-Fi connection failed. status={}'.format(wlan_status))
        raise RuntimeError(
            'Wi-Fi connection failed. status={}'.format(wlan_status))

    log('Wi-fi ready. ifconfig: {}'.format(wlan.ifconfig()))
    return wlan
