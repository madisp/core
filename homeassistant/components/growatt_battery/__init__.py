"""The Growatt battery controller integration."""
from __future__ import annotations
from homeassistant.components.growatt_battery.growatt_battery import GrowattBattery

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

ATTR_NAME = "name"
DEFAULT_NAME = "[]"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Growatt battery controller from a config entry."""

    async def handle_config_battery(call):
        input = call.data.get(ATTR_NAME, DEFAULT_NAME)
        if len(input) < 24:
            return

        charge_start = 2
        charge_price = 1000
        load_start = 19
        load_price = 0

        for idx, value in enumerate(input):
            if idx < 11 and (input[idx] + input[idx + 1]) < charge_price:
                charge_start = idx
                charge_price = input[idx] + input[idx + 1]
            if (
                12 <= idx < 20
                and (input[idx] + input[idx + 1] + input[idx + 2] + input[idx + 3])
                > load_price
            ):
                load_start = idx
                load_price = (
                    input[idx] + input[idx + 1] + input[idx + 2] + input[idx + 3]
                )

        hass.states.set("growatt.charge_time", "%02d:00" % charge_start)
        hass.states.set("growatt.load_time", "%02d:00" % load_start)

        username = entry.data["username"]
        password = entry.data["password"]
        api = await GrowattBattery.with_login(hass, username, password)

        if api is None:
            return

        plant_id = entry.data["plant_id"]
        device = entry.data["device"]
        await api.set_times(plant_id, device, charge_start, load_start)

    await hass.services.async_register(DOMAIN, "config_charge", handle_config_battery)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.services.async_remove(DOMAIN, "config_charge")
