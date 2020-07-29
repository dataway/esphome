import esphome.codegen as cg
from esphome.components import esp32_ble_tracker, sensor
import esphome.config_validation as cv
from esphome.const import (
    CONF_CONDUCTIVITY, CONF_ID, CONF_MAC_ADDRESS, CONF_MOISTURE, ICON_FLOWER, ICON_WATER_PERCENT,
    UNIT_MICROSIEMENS_PER_CENTIMETER, UNIT_PERCENT,
)

DEPENDENCIES = ['esp32_ble_tracker']
AUTO_LOAD = ['xiaomi_ble']

xiaomi_hhccpot002_ns = cg.esphome_ns.namespace('xiaomi_hhccpot002')
XiaomiHHCCPOT002 = xiaomi_hhccpot002_ns.class_('XiaomiHHCCPOT002',
                                               esp32_ble_tracker.ESPBTDeviceListener, cg.Component)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(XiaomiHHCCPOT002),
    cv.Required(CONF_MAC_ADDRESS): cv.mac_address,
    cv.Optional(CONF_MOISTURE): sensor.sensor_schema(UNIT_PERCENT, ICON_WATER_PERCENT, 0),
    cv.Optional(CONF_CONDUCTIVITY):
        sensor.sensor_schema(UNIT_MICROSIEMENS_PER_CENTIMETER, ICON_FLOWER, 0),
}).extend(esp32_ble_tracker.ESP_BLE_DEVICE_SCHEMA).extend(cv.COMPONENT_SCHEMA)


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    yield cg.register_component(var, config)
    yield esp32_ble_tracker.register_ble_device(var, config)

    cg.add(var.set_address(config[CONF_MAC_ADDRESS].as_hex))

    if CONF_MOISTURE in config:
        sens = yield sensor.new_sensor(config[CONF_MOISTURE])
        cg.add(var.set_moisture(sens))
    if CONF_CONDUCTIVITY in config:
        sens = yield sensor.new_sensor(config[CONF_CONDUCTIVITY])
        cg.add(var.set_conductivity(sens))
