"""Entity representing a Goal Zero Yeti device."""

from goalzero import Yeti

from homeassistant.const import ATTR_MODEL, CONF_NAME
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, MANUFACTURER
from .coordinator import GoalZeroDataUpdateCoordinator


class GoalZeroEntity(CoordinatorEntity[GoalZeroDataUpdateCoordinator]):
    """Representation of a Goal Zero Yeti entity."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: GoalZeroDataUpdateCoordinator,
        description: EntityDescription,
    ) -> None:
        """Initialize a Goal Zero Yeti entity."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.entity_description = description
        self._attr_name = (
            f"{coordinator.config_entry.data[CONF_NAME]} {description.name}"
        )
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}/{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device information of the entity."""
        return DeviceInfo(
            connections={(dr.CONNECTION_NETWORK_MAC, self._api.sysdata["macAddress"])},
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            manufacturer=MANUFACTURER,
            model=self._api.sysdata[ATTR_MODEL],
            name=self.coordinator.config_entry.data[CONF_NAME],
            sw_version=self._api.data["firmwareVersion"],
        )

    @property
    def _api(self) -> Yeti:
        """Return api from coordinator."""
        return self.coordinator.api
