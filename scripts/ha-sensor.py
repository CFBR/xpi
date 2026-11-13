# ha-sensor.py — show one Home Assistant or MQTT sensor.
#
# State:
#   sensor_source  ha or mqtt, default ha unless mqtt_topic is set
#   ha_url         Home Assistant base URL
#   ha_entity      entity id, for example sensor.living_room_temperature
#   mqtt_host      MQTT broker host
#   mqtt_port      MQTT broker port, default 1883
#   mqtt_topic     topic to subscribe to
#   mqtt_user      MQTT username, optional
#   sensor_name    label when the source has no friendly name
#   sensor_unit    unit when the source has no unit
#   sensor_refresh seconds between Home Assistant reads, minimum 10
#
# Secrets live in config.json as "ha_token" and "mqtt_password". MQTT needs
# the optional paho-mqtt module.

import json
import time
import urllib.parse
import urllib.request

import _display
import _dot
import _xpi_config
import _xpi_state

DEFAULT_COLOR = (0, 255, 0)
EMPTY = {"value": "--", "unit": "", "name": "sensor"}


def source():
    value = str(_xpi_state.value("sensor_source") or "").strip().lower()
    if value in ("ha", "mqtt"):
        return value
    return "mqtt" if _xpi_state.value("mqtt_topic") else "ha"


def refresh_seconds():
    try:
        return max(10, int(_xpi_state.value("sensor_refresh") or 30))
    except (TypeError, ValueError):
        return 30


def ha_fetch(previous):
    url = str(_xpi_state.value("ha_url") or "").rstrip("/")
    entity = str(_xpi_state.value("ha_entity") or "").strip()
    if not url or not entity:
        print("ha-sensor.py: set ha_url and ha_entity")
        return previous
    token = _xpi_config.value("ha_token")
    headers = {"Accept": "application/json", "User-Agent": "xpi"}
    if token:
        headers["Authorization"] = "Bearer " + str(token)
    request = urllib.request.Request(
        "%s/api/states/%s" % (url, urllib.parse.quote(entity, safe="")),
        headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.load(response)
    except Exception as exc:
        print("ha-sensor.py: fetch failed:", exc)
        return previous
    attributes = data.get("attributes") or {}
    value = str(data.get("state") or "").strip()
    if not value:
        return previous
    unit = str(attributes.get("unit_of_measurement")
               or _xpi_state.value("sensor_unit") or "")
    name = str(attributes.get("friendly_name")
               or _xpi_state.value("sensor_name") or entity)
    result = {"value": value, "unit": unit, "name": name}
    print("ha-sensor.py: %s = %s %s" % (name, value, unit))
    return result


def short_value(data):
    value = str(data.get("value") or "--").strip()
    unit = str(data.get("unit") or "").strip()
    try:
        number = float(value)
        if abs(number) >= 1000:
            value = _display.format_count(int(round(number)))
        elif number == int(number):
            value = str(int(number))
        else:
            value = "%.1f" % number
    except ValueError:
        pass
    unit = unit.replace("°", "").replace(" ", "")
    text = (value + unit).upper()
    return text[:6] or "--"


def unicorn_text(text):
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-:_ ")
    return "".join(ch if ch in allowed else " " for ch in text.upper())


def summary(data):
    text = "%s %s" % (data.get("name") or "sensor", short_value(data))
    return unicorn_text(text.replace("%", "PCT"))


def make_getter(fetch, interval):
    state = {"data": dict(EMPTY), "last": 0.0}

    def get():
        now = time.time()
        if now - state["last"] >= interval:
            state["data"] = fetch(state["data"])
            state["last"] = now
        return state["data"]

    return get


def run_microdot(getter):
    import microdotphat

    print("ha-sensor.py: microdot-phat")
    while True:
        microdotphat.clear()
        _dot.big_text(short_value(getter()))
        microdotphat.show()
        time.sleep(1)


def run_unicorn(getter):
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    data = getter()
    grid = _display.text_bitmap(summary(data))
    offset = 0
    last = None
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    print("ha-sensor.py: unicorn", shape)
    while True:
        data = getter()
        key = (data.get("value"), data.get("unit"), data.get("name"))
        if key != last:
            grid = _display.text_bitmap(summary(data))
            offset = 0
            last = key
            color = _display.parse_color(
                _xpi_state.value("color"), DEFAULT_COLOR)
        _display.draw_unicorn(grid, offset, shape, color)
        offset += 1
        time.sleep(0.05)


def run_ha():
    getter = make_getter(ha_fetch, refresh_seconds())
    return run_display(getter)


class MqttSensor:
    def __init__(self):
        import paho.mqtt.client as mqtt

        host = str(_xpi_state.value("mqtt_host") or "").strip()
        topic = str(_xpi_state.value("mqtt_topic") or "").strip()
        if not host or not topic:
            raise ValueError("set mqtt_host and mqtt_topic")
        try:
            port = int(_xpi_state.value("mqtt_port") or 1883)
        except (TypeError, ValueError):
            port = 1883
        self.data = dict(EMPTY)
        self.name = str(_xpi_state.value("sensor_name") or topic)
        self.unit = str(_xpi_state.value("sensor_unit") or "")
        self.client = mqtt.Client()
        user = _xpi_state.value("mqtt_user")
        password = _xpi_config.value("mqtt_password")
        if user:
            self.client.username_pw_set(str(user), str(password or ""))
        self.client.on_message = self.on_message
        self.client.connect(host, port, 30)
        self.client.subscribe(topic)
        self.client.loop_start()
        print("ha-sensor.py: mqtt", host, topic)

    def on_message(self, client, userdata, message):
        value = message.payload.decode("utf-8", "replace").strip()
        self.data = {"value": value, "unit": self.unit, "name": self.name}

    def get(self):
        return self.data

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()


def run_mqtt():
    try:
        sensor = MqttSensor()
    except ImportError:
        print("ha-sensor.py: MQTT needs paho-mqtt")
        raise SystemExit(1)
    except Exception as exc:
        print("ha-sensor.py: MQTT failed:", exc)
        raise SystemExit(1)
    try:
        return run_display(sensor.get)
    finally:
        sensor.close()


def run_display(getter):
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot(getter)
    except Exception as exc:
        print("ha-sensor.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("ha-sensor.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn(getter)


def main():
    if source() == "mqtt":
        return run_mqtt()
    return run_ha()


if __name__ == "__main__":
    main()
