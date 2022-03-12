"""
A bunch of helper methods to interface with Growatt's http APIs.
"""

import json
import requests
from urllib.parse import quote
from urllib.parse import quote_plus


GROWATT_DOMAIN = "server.growatt.com"
LOGIN_URL = f"https://{GROWATT_DOMAIN}/login"
TCP_SET_URL = f"https://{GROWATT_DOMAIN}/tcpSet.do"


class GrowattBattery:
    def __init__(self, session):
        self.session = session

    def login(self, username, password):
        """
        Attempt to login with the provided username and password, return false if fails
        """
        data = {"account": username, "password": password}
        resp = self.session.post(LOGIN_URL, data=data)
        return resp.status_code >= 200 and resp.status_code < 300

    def setTimes(self, plant, device, charge_start, discharge_start):
        """
        Set the charge and discharge times for the battery, based on hours 0-23.
        """
        memory_device_type = json.dumps([{"key": plant, "value": "mix"}]).replace(
            " ", ""
        )
        memory_device_sn = json.dumps(
            [{"key": plant, "value": "mix%" + device}]
        ).replace(" ", "")

        self.session.cookies.set("selectedPlantId", plant, domain=GROWATT_DOMAIN)
        self.session.cookies.set(
            "memoryDeviceType",
            quote_plus(memory_device_type),
            domain=GROWATT_DOMAIN,
        )
        self.session.cookies.set(
            "memoryDeviceSn", quote(memory_device_sn), domain=GROWATT_DOMAIN
        )

        resp = self.session.post(
            TCP_SET_URL,
            data={
                "action": "mixSet",
                "serialNum": device,
                "type": "mix_ac_charge_time_period",
                "param1": "90",
                "param2": "90",
                "param3": "1",
                "param4": "%02d" % charge_start,
                "param5": "00",
                "param6": "%02d" % discharge_start,
                "param7": "00",
                "param8": "1",
                "param9": "00",
                "param10": "00",
                "param11": "00",
                "param12": "00",
                "param13": "0",
                "param14": "00",
                "param15": "00",
                "param16": "00",
                "param17": "00",
                "param18": "0",
            },
        )
        return resp.status_code >= 200 and resp.status_code < 300

    @staticmethod
    def withLogin(username, password):
        """
        Create a new GrowattBattery instance using the provided credentials
        """
        api = GrowattBattery(requests.Session())

        if not api.login(username, password):
            return None

        return api
