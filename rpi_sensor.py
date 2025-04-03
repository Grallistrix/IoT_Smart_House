import network
import socket
import dht
import time
from machine import Pin, Timer

# HTML template
HTML = """\
HTTP/1.1 200 OK
Content-Type: text/plain
Connection: close

{}
"""

# Wi-Fi credentials
SSID = 'Test'
PASSWORD = 'Test'

# DHT sensor setup - Reading from Pin 22
dht_sensor = dht.DHT11(Pin(22))
led = Pin("LED", Pin.OUT)
vent = Pin(18, Pin.OUT)
TEMP_CORRECTION = -5
HUMID_COEFF = 0.5
temperature = None 
humidity = None

#=======================================================
def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print('Waiting for connection...')
        time.sleep(1)
    print('Connected:', wlan.ifconfig())

# Background task to update temperature adn humidity every 5s
def read_sensor(timer):
    global temperature, humidity
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature() + TEMP_CORRECTION
        humidity = dht_sensor.humidity() * HUMID_COEFF
        print(f'Temperature: {temperature}, Humidity: {humidity}')
    except OSError:
        temperature = "Error"
        humidity = "Error"

# Set up a timer to call `read_sensor` every 5s
temp_timer = Timer()
temp_timer.init(period=5000, mode=Timer.PERIODIC, callback=read_sensor)

connect()
led.value(0)

# Start server with proper socket cleanup
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print('Listening on', addr)

def handle_request():
    while True:
        try:
            cl, addr = s.accept()
            print('Client connected from', addr)
            request = cl.recv(1024).decode()
            
            if "GET /stats" in request:
                response = HTML.format(f"Temperature: {temperature}, Humidity: {humidity}")
            elif "GET /vent/on" in request:
                led.value(1)
                response = HTML.format("Ventilation ON")
            elif "GET /vent/off" in request:
                led.value(0)
                response = HTML.format("Ventilation OFF")
            else:
                response = HTML.format("Invalid endpoint")
            
            cl.send(response)
            cl.close()
        except OSError:
            cl.close()
            print('Connection closed')

handle_request()
