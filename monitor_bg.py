from datetime import datetime
from getpass import getpass
import os
import sys
import time
import logging

from pydexcom import Dexcom
from twilio.rest import Client
from pytz import timezone

logger = logging.getLogger('kea-bg-monitor')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def from_os_env_or_input(varname):
    if varname in os.environ:
        return os.environ[varname]
    return input(f"Enter {varname}:")



def local_time_now():
    return datetime.now(timezone(from_os_env_or_input("MY_TIMEZONE")))


def alert(bg):
    try:
        logger.info(f"alerting: {bg} at {local_time_now()}")
        account_sid = from_os_env_or_input("TWILIO_ACCOUNT_SID")
        auth_token = from_os_env_or_input("TWILIO_AUTH_TOKEN")
        client = Client(account_sid, auth_token)
        call = client.calls.create(
            url="http://demo.twilio.com/docs/voice.xml",
            to=from_os_env_or_input("MY_PHONE_NUMBER"),
            from_=from_os_env_or_input("TWILIO_PHONE_NUMBER"),
        )
        return local_time_now()
    except Exception as e:
        logger.error(f"Could not alert {e}")
        return None


dexcom_uname = from_os_env_or_input("MY_DEXCOM_USERNAME")
dexcom_pwd = getpass("Enter Dexom account pwd:")
cgm_update_interval_sec = 5 * 60
min_alert_interval_sec = 2 * 60 * 60
last_alerted_at = None
while True:
    alerted_recently = (
        last_alerted_at
        and (local_time_now() - last_alerted_at).seconds < min_alert_interval_sec
    )
    if not alerted_recently:
        try:
            bg = Dexcom(dexcom_uname, dexcom_pwd).get_current_glucose_reading()
            bg_is_recent = (
                datetime.now() - bg.time
            ).seconds < 10 * cgm_update_interval_sec
        except Exception as e:
            bg, bg_is_recent = None, False
            logger.error(f"Could not fetch BG {e}")
        if bg and bg_is_recent:
            logger.info(f"bg-info: {bg.time}, {bg.value}, {bg.trend}, {bg.trend_description}")

            if bg.value >= 100 and bg.trend_description in ("rising quickly"):
                last_alerted_at = alert(bg)
            elif bg.value >= 120 and bg.trend_description in (
                "rising",
                "rising quickly",
            ):
                last_alerted_at = alert(bg)
            elif bg.value >= 140 and bg.trend_description in (
                "rising slightly",
                "rising",
                "rising quickly",
            ):
                last_alerted_at = alert(bg)
            elif bg.value >= 160 and bg.trend_description in (
                "steady",
                "rising slightly",
                "rising",
                "rising quickly",
            ):
                last_alerted_at = alert(bg)
            elif bg.value <= 100 and bg.trend_description in ("falling quickly"):
                last_alerted_at = alert(bg)
            elif bg.value <= 80 and bg.trend_description in (
                "falling",
                "falling quickly",
            ):
                last_alerted_at = alert(bg)
            elif bg.value <= 70 and bg.trend_description in (
                "falling slightly",
                "falling",
                "falling quickly",
            ):
                last_alerted_at = alert(bg)
            elif bg.value <= 60 and bg.trend_description in (
                "steady",
                "falling slightly",
                "falling",
                "falling quickly",
            ):
                last_alerted_at = alert(bg)

    time.sleep(cgm_update_interval_sec)

