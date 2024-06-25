import ubinascii              # Conversions between binary data and various encodings
import machine                # To Generate a unique id from processor

WIFI_SSID = '****'
WIFI_PASS = '****'

AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = "HallinJR"
AIO_KEY = "****"
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
AIO_DOORS_FEED = "HallinJR/feeds/doors"