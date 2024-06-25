import machine
from machine import Pin, ADC
import time
import requests
from mqtt import MQTTClient    
import keys                  
import boot         


matches_counter = {}  # To keep track of the number of times each person is matched
# Try WiFi Connection
try:
    ip = boot.connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")

# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(keys.AIO_CLIENT_ID, keys.AIO_SERVER, keys.AIO_PORT, keys.AIO_USER, keys.AIO_KEY)
def message_callback(topic, msg):
    print(f"Received message on topic {topic}: {msg}")

# Set the newly defined callback function
client.set_callback(message_callback)
# Subscribed messages will be delivered to this callback
client.connect()
client.subscribe(keys.AIO_DOORS_FEED)


# Define GPIO pins
xPin = ADC(28)  # ADC0 on GPIO26
yPin = ADC(27)  # ADC1 on GPIO27
buttonPin = Pin(26, Pin.IN, Pin.PULL_UP)  # GPIO15 for button with pull-up

moves = []
last_move_time = None

def read_joystick():
    xVal = xPin.read_u16()  # Read X axis (16-bit value, range 0-65535)
    yVal = yPin.read_u16()  # Read Y axis (16-bit value, range 0-65535)
    buttonState = buttonPin.value()
    
    # Convert 16-bit values to 10-bit values (range 0-1023)
    xVal = xVal >> 6
    yVal = yVal >> 6
    
    return xVal, yVal, buttonState

def determine_move():
    x, y, button = read_joystick()
    if y > 950:
        return "Up"
    elif y < 90:
        return "Down"
    elif x < 100:
        return "Right"
    elif x > 900:
        return "Left"
    elif button == 0:
        return "Button Pressed"

def database():
    return {
        "Greta": ["Up", "Left", "Down", "Right", "Button Pressed"],
        "Elliot": ["Right", "Up", "Down", "Left"],
        "Baz": ["Down", "Right", "Up", "Up", "Left"],
        "Tilde": ["Button Pressed", "Up", "Down", "Down", "Right", "Left", "Button Pressed"]
    }

def check_input():
    global last_move_time
    current_move = determine_move()
    
    if current_move:
        current_time = time.time()
    
        if last_move_time is None or (current_time - last_move_time) >= 0.3:
            moves.append(current_move)
            last_move_time = current_time
            
            time.sleep(0.1)
    
    return moves


def is_sequence(sequence, moves):
    sequence_str = ','.join(sequence)
    moves_str = ','.join(moves)
    
    return sequence_str in moves_str

def send_to_adafruit(person):
    
    # Increment the person's count in the counter
    if person in matches_counter:
        matches_counter[person] += 1
    else:
        matches_counter[person] = 1

    # Prepare the message with the count
    topic = keys.AIO_DOORS_FEED  # Assuming you have a feed for doorbell events
    total_matches = sum(matches_counter.values())
    message = f"{person} is at the door now! Matched {matches_counter[person]} times.\n Total matches: {total_matches}"
    
    client.publish(topic, message)
    print(f"Sent to Adafruit IO: {message}")

def display():
    for person, sequence in database().items():
        if is_sequence(sequence, moves):
            send_discord_message(f"{person} is at the door now!")
            send_to_adafruit(person)  # Now also sends the count to Adafruit IO
            moves.clear()
            break

def send_discord_message(message):
    webhook_url = 'https://discord.com/api/webhooks/1255157455936032878/083IOxKv5pRt9xvAy7cCFfNEz-qj86HGwxNb2lKQqd3kKX-ZwGLDM7f8MSa3JJAm6L4_'
    data = {'content': message}
    response = requests.post(webhook_url, json=data)
    print(f"Message sent to Discord with response status code {response.status_code}")

while True:
    determine_move()
    check_input() 
    display() 
    current_time = time.time()
    if last_move_time is not None and (current_time - last_move_time) > 5:
        moves.clear()
        
        last_move_time = None