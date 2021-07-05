"""Test the Reload Patching Example config flow."""
from unittest.mock import patch

from homeassistant.components.async_reload_patch_mwe.const import DOMAIN
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


async def test_reloading(hass: HomeAssistant) -> None:
    """Test what happens when we reload via listener."""

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="abcde12345",
        title="Test Example",
        data={},
        options={"show_things": True},
    )
    with patch(
        "homeassistant.components.async_reload_patch_mwe.random",
        return_value=123456,
    ):
        config_entry.add_to_hass(hass)

        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    assert hass.data[DOMAIN][config_entry.entry_id] == 123456
    with patch(
        "homeassistant.components.async_reload_patch_mwe.random",
        return_value=654321,
    ), patch("homeassistant.config_entries.ConfigEntries.async_reload") as mock_reload:
        await hass.config_entries.async_reload(config_entry.entry_id)

        assert hass.data[DOMAIN][config_entry.entry_id] == 123456
        assert len(mock_reload.mock_calls) == 1

        result = await hass.config_entries.options.async_init(config_entry.entry_id)
        await hass.async_block_till_done()
        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"show_things": False},
        )
        assert result2["type"] == "create_entry"

        await hass.async_block_till_done()

        assert len(mock_reload.mock_calls) == 2

        assert hass.data[DOMAIN][config_entry.entry_id] == 123456
