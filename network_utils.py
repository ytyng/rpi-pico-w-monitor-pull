import rp2
import network
import settings
import utime


class WifiConnectionFailed(Exception):
    pass


class WifiConnectionAbort(Exception):
    pass


def prepare_wifi(log=None):
    for i in range(5):
        try:
            return _prepare_wifi(log=log)
        except WifiConnectionFailed as e:
            log('{}: {}', e.__class__.__name__, e)
            utime.sleep(2)
            continue
        except Exception as e:
            log('{}: {}', e.__class__.__name__, e)
            raise
    else:
        raise WifiConnectionAbort('Retry expired.')


def _prepare_wifi(log=None):
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
        if status < 0 or network.STAT_GOT_IP <= status:
            break
        log(f'Waiting ({i})... status={status}')
        utime.sleep(1)
    else:
        log('Wifi connection timed out.')
        raise WifiConnectionAbort('Wifi connection timed out.')

    # CYW43_LINK_DOWN (0)
    # CYW43_LINK_JOIN (1)
    # CYW43_LINK_NOIP (2)
    # CYW43_LINK_UP (3)
    # CYW43_LINK_FAIL (-1)
    # CYW43_LINK_NONET (-2)
    # CYW43_LINK_BADAUTH (-3)

    wlan_status = wlan.status()

    if wlan_status != network.STAT_GOT_IP:
        raise WifiConnectionFailed(
            'Wi-Fi connection failed. status={}'.format(wlan_status))

    log('Wi-fi ready. ifconfig: {}'.format(wlan.ifconfig()))
    return wlan
