from esphome import automation
from esphome.automation import Condition, maybe_simple_id
import esphome.codegen as cg
from esphome.components import mqtt
import esphome.config_validation as cv
from esphome.const import (
    CONF_ICON, CONF_ID, CONF_INTERNAL, CONF_INVERTED, CONF_MQTT_ID, CONF_NAME, CONF_ON_TURN_OFF,
    CONF_ON_TURN_ON, CONF_TRIGGER_ID,
)
from esphome.core import CORE, coroutine, coroutine_with_priority

CODEOWNERS = ['@esphome/core']
IS_PLATFORM_COMPONENT = True

switch_ns = cg.esphome_ns.namespace('switch_')
Switch = switch_ns.class_('Switch', cg.Nameable)
SwitchPtr = Switch.operator('ptr')

ToggleAction = switch_ns.class_('ToggleAction', automation.Action)
TurnOffAction = switch_ns.class_('TurnOffAction', automation.Action)
TurnOnAction = switch_ns.class_('TurnOnAction', automation.Action)
SwitchPublishAction = switch_ns.class_('SwitchPublishAction', automation.Action)

SwitchCondition = switch_ns.class_('SwitchCondition', Condition)
SwitchTurnOnTrigger = switch_ns.class_('SwitchTurnOnTrigger', automation.Trigger.template())
SwitchTurnOffTrigger = switch_ns.class_('SwitchTurnOffTrigger', automation.Trigger.template())

icon = cv.icon

SWITCH_SCHEMA = cv.MQTT_COMMAND_COMPONENT_SCHEMA.extend({
    cv.OnlyWith(CONF_MQTT_ID, 'mqtt'): cv.declare_id(mqtt.MQTTSwitchComponent),

    cv.Optional(CONF_ICON): icon,
    cv.Optional(CONF_INVERTED): cv.boolean,
    cv.Optional(CONF_ON_TURN_ON): automation.validate_automation({
        cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(SwitchTurnOnTrigger),
    }),
    cv.Optional(CONF_ON_TURN_OFF): automation.validate_automation({
        cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(SwitchTurnOffTrigger),
    }),
})


@coroutine
def setup_switch_core_(var, config):
    cg.add(var.set_name(config[CONF_NAME]))
    if CONF_INTERNAL in config:
        cg.add(var.set_internal(config[CONF_INTERNAL]))
    if CONF_ICON in config:
        cg.add(var.set_icon(config[CONF_ICON]))
    if CONF_INVERTED in config:
        cg.add(var.set_inverted(config[CONF_INVERTED]))
    for conf in config.get(CONF_ON_TURN_ON, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        yield automation.build_automation(trigger, [], conf)
    for conf in config.get(CONF_ON_TURN_OFF, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        yield automation.build_automation(trigger, [], conf)

    if CONF_MQTT_ID in config:
        mqtt_ = cg.new_Pvariable(config[CONF_MQTT_ID], var)
        yield mqtt.register_mqtt_component(mqtt_, config)


@coroutine
def register_switch(var, config):
    if not CORE.has_id(config[CONF_ID]):
        var = cg.Pvariable(config[CONF_ID], var)
    cg.add(cg.App.register_switch(var))
    yield setup_switch_core_(var, config)


SWITCH_ACTION_SCHEMA = maybe_simple_id({
    cv.Required(CONF_ID): cv.use_id(Switch),
})


@automation.register_action('switch.toggle', ToggleAction, SWITCH_ACTION_SCHEMA)
@automation.register_action('switch.turn_off', TurnOffAction, SWITCH_ACTION_SCHEMA)
@automation.register_action('switch.turn_on', TurnOnAction, SWITCH_ACTION_SCHEMA)
def switch_toggle_to_code(config, action_id, template_arg, args):
    paren = yield cg.get_variable(config[CONF_ID])
    yield cg.new_Pvariable(action_id, template_arg, paren)


@automation.register_condition('switch.is_on', SwitchCondition, SWITCH_ACTION_SCHEMA)
def switch_is_on_to_code(config, condition_id, template_arg, args):
    paren = yield cg.get_variable(config[CONF_ID])
    yield cg.new_Pvariable(condition_id, template_arg, paren, True)


@automation.register_condition('switch.is_off', SwitchCondition, SWITCH_ACTION_SCHEMA)
def switch_is_off_to_code(config, condition_id, template_arg, args):
    paren = yield cg.get_variable(config[CONF_ID])
    yield cg.new_Pvariable(condition_id, template_arg, paren, False)


@coroutine_with_priority(100.0)
def to_code(config):
    cg.add_global(switch_ns.using)
    cg.add_define('USE_SWITCH')
