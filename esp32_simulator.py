"""
Simulator ESP32 untuk Python di PC (Windows/Linux/Mac).
Mensimulasikan: sensor DHT22, relay GPIO 26, LED PWM GPIO 2.

Install dulu:  pip install paho-mqtt
Jalankan    :  python esp32_simulator.py
"""
import random
import time
import paho.mqtt.client as mqtt

# ===================== KONFIGURASI =====================
NIM = "2410010237"                      # <-- ganti dengan NIM kamu
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
INTERVAL = 3                     # detik

TOPIC_SUHU = f"iot/{NIM}/sensor/suhu"
TOPIC_RELAY = f"iot/{NIM}/aktuator/relay"
TOPIC_PWM = f"iot/{NIM}/aktuator/pwm"

relay_state = "OFF"   # simulasi GPIO 26
pwm_value = 0         # simulasi GPIO 2 (0-255)


def baca_suhu():
    """Simulasi DHT22: suhu acak 25.0 - 35.0 C"""
    return round(random.uniform(25.0, 35.0), 1)


def on_connect(client, userdata, flags, reason_code, properties=None):
    print("MQTT terhubung, kode:", reason_code)
    client.subscribe([(TOPIC_RELAY, 0), (TOPIC_PWM, 0)])


def on_message(client, userdata, msg):
    global relay_state, pwm_value
    pesan = msg.payload.decode().strip()

    if msg.topic == TOPIC_RELAY:
        if pesan.upper() in ("ON", "OFF"):
            relay_state = pesan.upper()
            print(f"[GPIO 26] Relay -> {relay_state}")

    elif msg.topic == TOPIC_PWM:
        try:
            pwm_value = max(0, min(255, int(float(pesan))))
            persen = round(pwm_value / 255 * 100)
            print(f"[GPIO 2 ] LED PWM -> {pwm_value} ({persen}%)")
        except ValueError:
            print("Nilai PWM tidak valid:", pesan)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

try:
    while True:
        suhu = baca_suhu()
        client.publish(TOPIC_SUHU, str(suhu))
        print(f"Suhu terkirim: {suhu} C | Relay: {relay_state} | PWM: {pwm_value}")
        time.sleep(INTERVAL)
except KeyboardInterrupt:
    print("Berhenti.")
    client.loop_stop()
    client.disconnect()
