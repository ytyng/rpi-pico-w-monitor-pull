"""
What to do between requests, selected by settings.POWER_MODE.

polling   : stay awake and sleep POLLING_TIME_SECONDS.
deepsleep : machine.deepsleep(DEEP_SLEEP_SECONDS). The USB REPL does not
            answer while sleeping, so deploying needs a replug + Ctrl-C.
tpl5110   : pulse DONE (TPL5110_DONE_PIN) so the TPL5110 cuts our power.
            The TPL5110's own resistor sets the next power-on time.
"""
import machine
import settings
import utime

MODES = ('polling', 'deepsleep', 'tpl5110')


def get_mode() -> str:
    # settings.py written before POWER_MODE existed only had DEEP_SLEEP_SECONDS.
    default = 'deepsleep' if getattr(settings, 'DEEP_SLEEP_SECONDS', None) \
        else 'polling'
    mode = getattr(settings, 'POWER_MODE', default)
    # A typo here would silently become polling; on a TPL5110 unit that means
    # DONE never fires and the battery drains.
    if mode not in MODES:
        raise ValueError('Unknown POWER_MODE: {!r}'.format(mode))
    return mode


def after_request(wlan):
    mode = get_mode()
    if mode == 'deepsleep':
        _deepsleep(wlan)
    elif mode == 'tpl5110':
        _tpl5110_done()
    _polling_sleep()


def on_startup_failure():
    """
    Give up this cycle. In tpl5110 mode cut our power so the TPL5110 retries
    on its next period; a plain reset would loop forever with Wi-Fi on.
    """
    if get_mode() == 'tpl5110':
        _tpl5110_done()
    machine.reset()


def _polling_sleep():
    utime.sleep(settings.POLLING_TIME_SECONDS)


def _deepsleep(wlan):
    print('Deep sleep for {} seconds.'.format(settings.DEEP_SLEEP_SECONDS))
    utime.sleep(1)
    wlan.disconnect()
    wlan.active(False)
    machine.Pin(23, machine.Pin.OUT).low()  # CYW43 power off
    # On RP2040 this resets the board on wake, so it never returns.
    machine.deepsleep(settings.DEEP_SLEEP_SECONDS * 1000)


def _tpl5110_done():
    pin_no = getattr(settings, 'TPL5110_DONE_PIN', 16)
    print('TPL5110 DONE on GP{}.'.format(pin_no))
    done = machine.Pin(pin_no, machine.Pin.OUT)
    done.high()
    utime.sleep_ms(100)
    done.low()
    # Power is cut here when the TPL5110 is wired. If we are still running
    # (USB attached, or no TPL5110), the caller falls back to polling so
    # the REPL stays reachable for deploys.
    utime.sleep(1)
    print('Still powered after DONE; falling back to polling.')
