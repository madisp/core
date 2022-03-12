"""
A bunch of helper methods to interface with Growatt's http APIs.
"""

import aiohttp
import json
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from urllib.parse import quote, quote_plus
from yarl import URL


GROWATT_DOMAIN = "server.growatt.com"
LOGIN_URL = f"https://{GROWATT_DOMAIN}/login"
TCP_SET_URL = f"https://{GROWATT_DOMAIN}/tcpSet.do"


class GrowattBattery:
    """
    A bunch of helper methods to control the charge/discharge times of a battery connected
    to a Growatt inverter.
    """

    def __init__(self, client: aiohttp.ClientSession) -> None:
        self.client = client

    async def login(self, username, password) -> bool:
        """
        Attempt to login with the provided username and password, return false if fails
        """
        data = {"account": username, "password": password}
        resp = await self.client.post(LOGIN_URL, data=data)
        return resp.status_code >= 200 and resp.status_code < 300

    async def set_times(self, plant, device, charge_start, discharge_start) -> bool:
        """
        Set the charge and discharge times for the battery, based on hours 0-23.
        """
        memory_device_type = json.dumps([{"key": plant, "value": "mix"}]).replace(
            " ", ""
        )
        memory_device_sn = json.dumps(
            [{"key": plant, "value": "mix%" + device}]
        ).replace(" ", "")

        self.client.cookie_jar.update_cookies(
            {
                "selectedPlantId": plant,
                "memoryDeviceType": quote_plus(memory_device_type),
                "memoryDeviceSn": quote(memory_device_sn),
            },
            URL(TCP_SET_URL),
        )

        resp = await self.client.post(
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
    async def with_login(
        hass: HomeAssistant, username: str, password: str
    ) -> GrowattBattery:
        """
        Create a new GrowattBattery instance using the provided credentials
        """
        api = GrowattBattery(async_get_clientsession(hass))

        if not await api.login(username, password):
            return None

        return api
