import esphome.codegen as cg
from esphome.components import fan, output
import esphome.config_validation as cv
from esphome.const import (
    CONF_DIRECTION_OUTPUT, CONF_OSCILLATION_OUTPUT, CONF_OUTPUT, CONF_OUTPUT_ID,
)

from .. import binary_ns

BinaryFan = binary_ns.class_('BinaryFan', cg.Component)

CONFIG_SCHEMA = fan.FAN_SCHEMA.extend({
    cv.GenerateID(CONF_OUTPUT_ID): cv.declare_id(BinaryFan),
    cv.Required(CONF_OUTPUT): cv.use_id(output.BinaryOutput),
    cv.Optional(CONF_DIRECTION_OUTPUT): cv.use_id(output.BinaryOutput),
    cv.Optional(CONF_OSCILLATION_OUTPUT): cv.use_id(output.BinaryOutput),
}).extend(cv.COMPONENT_SCHEMA)


def to_code(config):
    var = cg.new_Pvariable(config[CONF_OUTPUT_ID])
    yield cg.register_component(var, config)

    fan_ = yield fan.create_fan_state(config)
    cg.add(var.set_fan(fan_))
    output_ = yield cg.get_variable(config[CONF_OUTPUT])
    cg.add(var.set_output(output_))

    if CONF_OSCILLATION_OUTPUT in config:
        oscillation_output = yield cg.get_variable(config[CONF_OSCILLATION_OUTPUT])
        cg.add(var.set_oscillating(oscillation_output))

    if CONF_DIRECTION_OUTPUT in config:
        direction_output = yield cg.get_variable(config[CONF_DIRECTION_OUTPUT])
        cg.add(var.set_direction(direction_output))
