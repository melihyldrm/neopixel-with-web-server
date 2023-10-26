import network
import ure
import socket
import machine
import neopixel
import math
import time

#Enter the required information to connect to the Wi-Fi network
SSID = "yourWifiName"
PASSWORD = "yourWifiPassword"

# Wi-Fi ağına bağlan
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(SSID, PASSWORD)

# Check the connection
while not sta_if.isconnected():
    pass

# Print IP address after connecting
print("Bağlandı. IP adresi:", sta_if.ifconfig()[0])

#Define the pin number and number of LEDs in your NeoPixel strip
pin_num = 2
num_leds = 8

# Initialize the NeoPixel strip
np = neopixel.NeoPixel(machine.Pin(pin_num), num_leds)

#Variable to hold LED status
led_on = False

#IP address and port number of the web server
IP_ADDRESS = sta_if.ifconfig()[0]
PORT = 80

#Function that responds to HTTP GET request
def handle_request(request):
    global led_on
    if ure.search("GET /on", request):
        led_on = True
    elif ure.search("GET /off", request):
        led_on = False
    
    #Generate HTTP response
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
    response += "<html><body>"
    response += "<h1>LED Durumu: {}</h1>".format("Açık" if led_on else "Kapalı")
    response += "<a href='/on'><button>Aç</button></a>"
    response += "<a href='/off'><button>Kapat</button></a>"
    response += "</body></html>"
    
    return response

#Start web server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP_ADDRESS, PORT))
s.listen(5)
print("Web sunucusu çalışıyor. IP adresi:", IP_ADDRESS, "Port:", PORT)

offset=0.0

# Function to set rainbow colors on the LED strip
def set_rainbow_colors(offset):
    for i in range(num_leds):
        hue = ((i / num_leds) * 360.0 + offset) % 360.0  # Calculate the hue value based on the LED index and offset
        rgb = hsv_to_rgb(hue, 1.0, 1.0)  # Convert the HSV color to RGB color
        np[i] = rgb
    np.write()
    offset+=5
    time.sleep(2)
    
# Function to convert HSV color to RGB color
def hsv_to_rgb(h, s, v):
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)

#Accept connection to web server and process requests
while True:
    conn, addr = s.accept()
    request = conn.recv(1024)
    request = request.decode("utf-8")
    
    response = handle_request(request)
    
    conn.send(response)
    conn.close()
    
    #Update NeoPixel strip based on LED status
    if led_on:
        set_rainbow_colors(offset)
    else:
        np.fill((0, 0, 0))
        np.write()







