import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import (
    climate,
    uart,
    sensor,
    binary_sensor,
    button,
    text_sensor,
    select,
    switch,
)
from esphome.const import (
    CONF_CUSTOM_FAN_MODES,
    CONF_ID,
    CONF_NAME,
    CONF_OUTDOOR_TEMPERATURE,
    CONF_SENSORS,
    CONF_SUPPORTED_FAN_MODES,
    CONF_SUPPORTED_MODES,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_FREQUENCY,
    ENTITY_CATEGORY_CONFIG,
    ENTITY_CATEGORY_NONE,
    STATE_CLASS_MEASUREMENT,
    UNIT_CELSIUS,
    UNIT_HERTZ,
)
from esphome.core import coroutine

CODEOWNERS = ["@Sammy1Am", "@KazWolfe"]

AUTO_LOAD = [
    "climate",
    "select",
    "sensor",
    "binary_sensor",
    "button",
    "text_sensor",
    "switch",
]
DEPENDENCIES = [
    "uart",
    "climate",
    "sensor",
    "binary_sensor",
    "button",
    "text_sensor",
    "select",
    "switch",
]

CONF_UART_HEATPUMP = "uart_heatpump"
CONF_UART_THERMOSTAT = "uart_thermostat"

CONF_THERMOSTAT_TEMPERATURE = "thermostat_temperature"
CONF_ERROR_CODE = "error_code"
CONF_ISEE_STATUS = "isee_status"

CONF_SELECTS = "selects"
CONF_TEMPERATURE_SOURCE_SELECT = "temperature_source_select"  # This is to create a Select object for selecting a source
CONF_VANE_POSITION_SELECT = "vane_position_select"
CONF_HORIZONTAL_VANE_POSITION_SELECT = "horizontal_vane_position_select"

CONF_BUTTONS = "buttons"
CONF_FILTER_RESET_BUTTON = "filter_reset_button"

CONF_SWITCHES = "switches"
CONF_ZONE_0_SWITCH = "zone_0_switch"
CONF_ZONE_1_SWITCH = "zone_1_switch"
CONF_ZONE_2_SWITCH = "zone_2_switch"
CONF_ZONE_3_SWITCH = "zone_3_switch"
CONF_ZONE_4_SWITCH = "zone_4_switch"
CONF_ZONE_5_SWITCH = "zone_5_switch"
CONF_ZONE_6_SWITCH = "zone_6_switch"
CONF_ZONE_7_SWITCH = "zone_7_switch"

CONF_TEMPERATURE_SOURCES = (
    "temperature_sources"  # This is for specifying additional sources
)

CONF_DISABLE_ACTIVE_MODE = "disable_active_mode"

DEFAULT_POLLING_INTERVAL = "5s"

mitsubishi_itp_ns = cg.esphome_ns.namespace("mitsubishi_itp")
MitsubishiUART = mitsubishi_itp_ns.class_(
    "MitsubishiUART", cg.PollingComponent, climate.Climate
)

TemperatureSourceSelect = mitsubishi_itp_ns.class_(
    "TemperatureSourceSelect", select.Select
)
VanePositionSelect = mitsubishi_itp_ns.class_("VanePositionSelect", select.Select)
HorizontalVanePositionSelect = mitsubishi_itp_ns.class_(
    "HorizontalVanePositionSelect", select.Select
)

FilterResetButton = mitsubishi_itp_ns.class_(
    "FilterResetButton", button.Button, cg.Component
)

Zone0Switch = mitsubishi_itp_ns.class_("Zone0Switch", switch.Switch, cg.Component)
Zone1Switch = mitsubishi_itp_ns.class_("Zone1Switch", switch.Switch, cg.Component)
Zone2Switch = mitsubishi_itp_ns.class_("Zone2Switch", switch.Switch, cg.Component)
Zone3Switch = mitsubishi_itp_ns.class_("Zone3Switch", switch.Switch, cg.Component)
Zone4Switch = mitsubishi_itp_ns.class_("Zone4Switch", switch.Switch, cg.Component)
Zone5Switch = mitsubishi_itp_ns.class_("Zone5Switch", switch.Switch, cg.Component)
Zone6Switch = mitsubishi_itp_ns.class_("Zone6Switch", switch.Switch, cg.Component)
Zone7Switch = mitsubishi_itp_ns.class_("Zone7Switch", switch.Switch, cg.Component)

DEFAULT_CLIMATE_MODES = ["OFF", "HEAT", "DRY", "COOL", "FAN_ONLY", "HEAT_COOL"]
DEFAULT_FAN_MODES = ["AUTO", "QUIET", "LOW", "MEDIUM", "HIGH"]
CUSTOM_FAN_MODES = {"VERYHIGH": mitsubishi_itp_ns.FAN_MODE_VERYHIGH}
VANE_POSITIONS = ["Auto", "1", "2", "3", "4", "5", "Swing"]
HORIZONTAL_VANE_POSITIONS = ["Auto", "<<", "<", "|", ">", ">>", "<>", "Swing"]

INTERNAL_TEMPERATURE_SOURCE_OPTIONS = [
    mitsubishi_itp_ns.TEMPERATURE_SOURCE_INTERNAL
]  # These will always be available

validate_custom_fan_modes = cv.enum(CUSTOM_FAN_MODES, upper=True)

BASE_SCHEMA = climate.CLIMATE_SCHEMA.extend(
    {
        cv.GenerateID(CONF_ID): cv.declare_id(MitsubishiUART),
        cv.Required(CONF_UART_HEATPUMP): cv.use_id(uart.UARTComponent),
        cv.Optional(CONF_UART_THERMOSTAT): cv.use_id(uart.UARTComponent),
        # Overwrite name from ENTITY_BASE_SCHEMA with "Climate" as default
        cv.Optional(CONF_NAME, default="Climate"): cv.Any(
            cv.All(
                cv.none,
                cv.requires_friendly_name(
                    "Name cannot be None when esphome->friendly_name is not set!"
                ),
            ),
            cv.string,
        ),
        cv.Optional(
            CONF_SUPPORTED_MODES, default=DEFAULT_CLIMATE_MODES
        ): cv.ensure_list(climate.validate_climate_mode),
        cv.Optional(
            CONF_SUPPORTED_FAN_MODES, default=DEFAULT_FAN_MODES
        ): cv.ensure_list(climate.validate_climate_fan_mode),
        cv.Optional(CONF_CUSTOM_FAN_MODES, default=["VERYHIGH"]): cv.ensure_list(
            validate_custom_fan_modes
        ),
        cv.Optional(CONF_TEMPERATURE_SOURCES, default=[]): cv.ensure_list(
            cv.use_id(sensor.Sensor)
        ),
        cv.Optional(CONF_DISABLE_ACTIVE_MODE, default=False): cv.boolean,
    }
).extend(cv.polling_component_schema(DEFAULT_POLLING_INTERVAL))

# TODO Storing the registration function here seems weird, but I can't figure out how to determine schema type later
SENSORS = dict[str, tuple[str, cv.Schema, callable]](
    {
        CONF_THERMOSTAT_TEMPERATURE: (
            "Thermostat Temperature",
            sensor.sensor_schema(
                unit_of_measurement=UNIT_CELSIUS,
                device_class=DEVICE_CLASS_TEMPERATURE,
                state_class=STATE_CLASS_MEASUREMENT,
                accuracy_decimals=1,
            ),
            sensor.register_sensor,
        ),
        CONF_OUTDOOR_TEMPERATURE: (
            "Outdoor Temperature",
            sensor.sensor_schema(
                unit_of_measurement=UNIT_CELSIUS,
                device_class=DEVICE_CLASS_TEMPERATURE,
                state_class=STATE_CLASS_MEASUREMENT,
                accuracy_decimals=1,
                icon="mdi:sun-thermometer-outline",
            ),
            sensor.register_sensor,
        ),
        "compressor_frequency": (
            "Compressor Frequency",
            sensor.sensor_schema(
                unit_of_measurement=UNIT_HERTZ,
                device_class=DEVICE_CLASS_FREQUENCY,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
            sensor.register_sensor,
        ),
        "actual_fan": (
            "Actual Fan Speed",
            text_sensor.text_sensor_schema(
                icon="mdi:fan",
            ),
            text_sensor.register_text_sensor,
        ),
        "filter_status": (
            "Filter Status",
            binary_sensor.binary_sensor_schema(
                device_class="problem", icon="mdi:air-filter"
            ),
            binary_sensor.register_binary_sensor,
        ),
        "defrost": (
            "Defrost",
            binary_sensor.binary_sensor_schema(icon="mdi:snowflake-melt"),
            binary_sensor.register_binary_sensor,
        ),
        "preheat": (
            "Preheat",
            binary_sensor.binary_sensor_schema(icon="mdi:heating-coil"),
            binary_sensor.register_binary_sensor,
        ),
        "standby": (
            "Standby",
            binary_sensor.binary_sensor_schema(icon="mdi:pause-circle-outline"),
            binary_sensor.register_binary_sensor,
        ),
        CONF_ISEE_STATUS: (
            "i-see Status",
            binary_sensor.binary_sensor_schema(icon="mdi:eye"),
            binary_sensor.register_binary_sensor,
        ),
        CONF_ERROR_CODE: (
            "Error Code",
            text_sensor.text_sensor_schema(icon="mdi:alert-circle-outline"),
            text_sensor.register_text_sensor,
        ),
    }
)

SENSORS_SCHEMA = cv.All(
    {
        cv.Optional(
            sensor_designator,
            default={"name": f"{sensor_name}", "disabled_by_default": "true"},
        ): sensor_schema
        for sensor_designator, (
            sensor_name,
            sensor_schema,
            registration_function,
        ) in SENSORS.items()
    }
)

SELECTS = {
    CONF_TEMPERATURE_SOURCE_SELECT: (
        "Temperature Source",
        select.select_schema(
            TemperatureSourceSelect,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:thermometer-check",
        ),
        INTERNAL_TEMPERATURE_SOURCE_OPTIONS,
    ),
    CONF_VANE_POSITION_SELECT: (
        "Vane Position",
        select.select_schema(
            VanePositionSelect,
            entity_category=ENTITY_CATEGORY_NONE,
            icon="mdi:arrow-expand-vertical",
        ),
        VANE_POSITIONS,
    ),
    CONF_HORIZONTAL_VANE_POSITION_SELECT: (
        "Horizontal Vane Position",
        select.select_schema(
            HorizontalVanePositionSelect,
            entity_category=ENTITY_CATEGORY_NONE,
            icon="mdi:arrow-expand-horizontal",
        ),
        HORIZONTAL_VANE_POSITIONS,
    ),
}

SELECTS_SCHEMA = cv.All(
    {
        cv.Optional(
            select_designator, default={"name": f"{select_name}"}
        ): select_schema
        for select_designator, (
            select_name,
            select_schema,
            select_options,
        ) in SELECTS.items()
    }
)

BUTTONS = {
    CONF_FILTER_RESET_BUTTON: (
        "Filter Reset",
        button.button_schema(
            FilterResetButton,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:restore",
        ),
    )
}

BUTTONS_SCHEMA = cv.All(
    {
        cv.Optional(
            button_designator, default={"name": f"{button_name}"}
        ): button_schema
        for button_designator, (button_name, button_schema) in BUTTONS.items()
    }
)

SWITCHES = {
    CONF_ZONE_0_SWITCH: (
        "Zone 0",
        switch.switch_schema(Zone0Switch, entity_category=ENTITY_CATEGORY_CONFIG),
    ),
    CONF_ZONE_1_SWITCH: (
        "Zone 1",
        switch.switch_schema(Zone1Switch, entity_category=ENTITY_CATEGORY_CONFIG),
    ),
    CONF_ZONE_2_SWITCH: (
        "Zone 2",
        switch.switch_schema(Zone2Switch, entity_category=ENTITY_CATEGORY_CONFIG),
    ),
    CONF_ZONE_3_SWITCH: (
        "Zone 3",
        switch.switch_schema(Zone3Switch, entity_category=ENTITY_CATEGORY_CONFIG),
    ),
    CONF_ZONE_4_SWITCH: (
        "Zone 4",
        switch.switch_schema(Zone4Switch, entity_category=ENTITY_CATEGORY_CONFIG),
    ),
    CONF_ZONE_5_SWITCH: (
        "Zone 5",
        switch.switch_schema(Zone5Switch, entity_category=ENTITY_CATEGORY_CONFIG),
    ),
    CONF_ZONE_6_SWITCH: (
        "Zone 6",
        switch.switch_schema(Zone6Switch, entity_category=ENTITY_CATEGORY_CONFIG),
    ),
    CONF_ZONE_7_SWITCH: (
        "Zone 7",
        switch.switch_schema(Zone7Switch, entity_category=ENTITY_CATEGORY_CONFIG),
    ),
}

SWITCHES_SCHEMA = cv.All(
    {
        cv.Optional(
            switch_designator, default={"name": f"{switch_name}"}
        ): switch_schema
        for switch_designator, (switch_name, switch_schema) in SWITCHES.items()
    }
)

CONFIG_SCHEMA = BASE_SCHEMA.extend(
    {
        cv.Optional(CONF_SENSORS, default={}): SENSORS_SCHEMA,
        cv.Optional(CONF_SELECTS, default={}): SELECTS_SCHEMA,
        cv.Optional(CONF_BUTTONS, default={}): BUTTONS_SCHEMA,
        cv.Optional(CONF_SWITCHES, default={}): SWITCHES_SCHEMA,
    }
)


@coroutine
async def to_code(config):
    hp_uart_component = await cg.get_variable(config[CONF_UART_HEATPUMP])
    muart_component = cg.new_Pvariable(config[CONF_ID], hp_uart_component)

    await cg.register_component(muart_component, config)
    await climate.register_climate(muart_component, config)

    # If thermostat defined
    if CONF_UART_THERMOSTAT in config:
        # Register thermostat with MUART
        ts_uart_component = await cg.get_variable(config[CONF_UART_THERMOSTAT])
        cg.add(getattr(muart_component, "set_thermostat_uart")(ts_uart_component))
        # Add sensor as source
        SELECTS[CONF_TEMPERATURE_SOURCE_SELECT][2].append("Thermostat")

    # Traits

    traits = muart_component.config_traits()

    if CONF_SUPPORTED_MODES in config:
        cg.add(traits.set_supported_modes(config[CONF_SUPPORTED_MODES]))

    if CONF_SUPPORTED_FAN_MODES in config:
        cg.add(traits.set_supported_fan_modes(config[CONF_SUPPORTED_FAN_MODES]))

    if CONF_CUSTOM_FAN_MODES in config:
        cg.add(traits.set_supported_custom_fan_modes(config[CONF_CUSTOM_FAN_MODES]))

    # Sensors

    for sensor_designator, (
        _,
        _,
        registration_function,
    ) in SENSORS.items():
        # Only add the thermostat temp if we have a TS_UART
        if (sensor_designator == CONF_THERMOSTAT_TEMPERATURE) and (
            CONF_UART_THERMOSTAT not in config
        ):
            continue

        sensor_conf = config[CONF_SENSORS][sensor_designator]
        sensor_component = cg.new_Pvariable(sensor_conf[CONF_ID])

        await registration_function(sensor_component, sensor_conf)

        cg.add(
            getattr(muart_component, f"set_{sensor_designator}_sensor")(
                sensor_component
            )
        )

    # Selects

    # Add additional configured temperature sensors to the select menu
    for ts_id in config[CONF_TEMPERATURE_SOURCES]:
        ts = await cg.get_variable(ts_id)
        SELECTS[CONF_TEMPERATURE_SOURCE_SELECT][2].append(ts.get_name())
        cg.add(
            getattr(ts, "add_on_state_callback")(
                # TODO: Is there anyway to do this without a raw expression?
                cg.RawExpression(
                    f"[](float v){{{getattr(muart_component, 'temperature_source_report')}({ts.get_name()}, v);}}"
                )
            )
        )

    # Register selects
    for select_designator, (
        _,
        _,
        select_options,
    ) in SELECTS.items():
        select_conf = config[CONF_SELECTS][select_designator]
        select_component = cg.new_Pvariable(select_conf[CONF_ID])
        cg.add(getattr(muart_component, f"set_{select_designator}")(select_component))
        await cg.register_parented(select_component, muart_component)

        # For temperature source select, skip registration if there are less than two sources
        if select_designator == CONF_TEMPERATURE_SOURCE_SELECT:
            if len(SELECTS[CONF_TEMPERATURE_SOURCE_SELECT][2]) < 2:
                continue

        await select.register_select(
            select_component, select_conf, options=select_options
        )

    # Buttons
    for button_designator, (_, _) in BUTTONS.items():
        button_conf = config[CONF_BUTTONS][button_designator]
        button_component = await button.new_button(button_conf)
        await cg.register_component(button_component, button_conf)
        await cg.register_parented(button_component, muart_component)

    # Switches
    for switch_designator, (_, _) in SWITCHES.items():
        switch_conf = config[CONF_SWITCHES][switch_designator]
        switch_component = await switch.new_switch(switch_conf)
        await cg.register_component(switch_component, switch_conf)
        await cg.register_parented(switch_component, muart_component)

    # Debug Settings
    if dam_conf := config.get(CONF_DISABLE_ACTIVE_MODE):
        cg.add(getattr(muart_component, "set_active_mode")(not dam_conf))
