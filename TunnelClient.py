import cv2
import pyautogui
import time
import pyperclip
import os 
import hashlib
import base64
import socket
from enum import Enum
### Notes ###
# pip install opencv-python, pyautogui, pyperclip, hashlib
# IMPORTANT set chat background to black, uncheck "Add whatsapp doodles"
# Decoding and cutting the '*' will be handled by the function that calls read_message()

# Globals
cliphash = ""
new_message_x = 0
new_message_y = 0
text_box_x = 0
text_box_y = 0
delay = .05
HOST = ''
PORT = 44455
BUFFER_SIZE = 1024

# Enum for message senders
class Sender(Enum):
    self = 0
    server = 1
    ack = 2

# Enum for message colors
class Color(Enum):
    green = (5, 97, 98)
    grey = (38, 45, 49)
    black = (10, 12, 13)

### Runs on startup to find essential GUI object coordinates ###   
def find_coords():
    # Take the screenshot to look for coords in
    pyautogui.screenshot('./assets/ss.png')

    # Resize the WhatsApp window
    resize()
    os.remove('./assets/ss.png')
    pyautogui.screenshot('./assets/ss.png')
    
    # Find coords of gui objects
    find_new_message()
    find_text_box()

    # Remove screenshot
    os.remove('assets/ss.png')

### Resize the WhatsApp window to make it easier to find the newest message coords easier ###
def resize():
    # Get coords to change window size
    method = cv2.TM_SQDIFF_NORMED
    small_image = cv2.imread('./assets/resize.png')
    large_image = cv2.imread('./assets/ss.png')
    result = cv2.matchTemplate(small_image, large_image, method)
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)
    X, Y = mnLoc
    
    # Drag the window all the way to the left
    pyautogui.moveTo(X + 50, Y)
    pyautogui.dragTo(0, Y)
    pyautogui.press('pagedown')
    pyautogui.press('pagedown')
    pyautogui.press('pagedown')
    pyautogui.press('pagedown')

### Finds the coordinates of the textbox to write messages ###
def find_text_box():
    global text_box_x
    global text_box_y

    method = cv2.TM_SQDIFF_NORMED
    small_image = cv2.imread('./assets/textbox.png')
    large_image = cv2.imread('./assets/ss.png')
    result = cv2.matchTemplate(small_image, large_image, method)
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)
    text_box_x, text_box_y = mnLoc

### Finds the spot we can triple click to copy the newest message ###
def find_new_message():
    global new_message_x
    global new_message_y

    method = cv2.TM_SQDIFF_NORMED
    small_image = cv2.imread('./assets/new_message.png')
    large_image = cv2.imread('./assets/ss.png')
    result = cv2.matchTemplate(small_image, large_image, method)
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)
    new_message_x, new_message_y = mnLoc

### Writes a message to WhatsApp ###
def write_message(message):
    # Click on the text box
    pyautogui.click(text_box_x,text_box_y)
    # Base64encode message and append a * so receiver knows when we're done
    b64message = base64.b64encode(message) + '*'.encode('utf-8')
    # Send the messages in 844 character chunks
    while(len(b64message.decode("utf-8")) > 844):
        # make curr_chunk string the first 844 characters of b64message
        curr_chunk = b64message[:844]
        # Remove the characters in the ToSend string
        b64message = b64message[845:]
        # write the message in the text box
        pyautogui.write(curr_chunk.decode('utf-8'))

        pyautogui.press('enter')
        # Wait for an ack
        wait_ack()

    # write the message to the box
    pyautogui.write(b64message.decode("utf-8"))
    # click send
    pyautogui.press('enter')

# Check for new messages
# Returns who sent the most recent message (self, server, ack)
def most_recent_sender():
    # Try until it works because the pyautogui pixel function is broken sometimes
    while True:
        try:
            # Checks if a pixel in the newest message is green (self), grey (server), black (ACK from either party)
            color = pyautogui.pixel((new_message_x + 90), (new_message_y - 30))
            switch (color) {
                case Color.green:
                    return Sender.self
                case Color.grey:
                    return Sender.server
                case Color.black:
                    return Sender.ack
            }
        except:
            print("pyautogui machine broke")

### Attempts to read the newest message ###
### Returns: Returns newest message if not from self ###
def read_message():

    # Check who sent the most recent message
    sender = most_recent_sender():

    if sender == Sender.server:
        return None
    else if sender == Sender.ack:
        return "Ack"

    # Get the new message by copying it
    highlight_new_message()
    pyautogui.hotkey('ctrl', 'c')
    pyautogui.press('esc')
    new_message = pyperclip.paste()
    return new_message

def highlight_new_message():
    pyautogui.click(new_message_x -11, new_message_y - 30)
    pyautogui.click(new_message_x -11, new_message_y - 30)
    pyautogui.click(new_message_x -11, new_message_y - 30)

### Waits for the next full message to come in ###
### Acks and decodes as necessary ###
def wait_full_message():
    # Wait for a response from server
    message = read_message()

    while message is None or len(message) < 1:
        time.sleep(delay)
        message = read_message()

    while message[-1] != '*':
        write_ack()
        next_chunk = read_message()
        while next_chunk is None:
            time.sleep(delay)
            next_chunk = read_message()
        message += next_chunk

    return base64.b64decode(message[:-1]).decode('utf-8')

### Wait for other side to ack ###
### ACKS are only sent and read by write_message ###
def wait_ack():
    while read_message() != "Ack":
        time.sleep(delay)

### Send ACK ###
def write_ack():
    # Click on the text box
    pyautogui.click(text_box_x,text_box_y)
    # Write ACK
    pyautogui.write("Ack")
    # click send
    pyautogui.press('enter')

### Proxy functions ###
def start():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        
        while True:
            conn, addr = s.accept()
            print('Connection from ', addr)
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            if "cern" in data.decode('utf-8'):
                tunnel_request(data, conn)

def tunnel_request(data, conn):
    # Writes WhatsApp message
    write_message(data)
    # Wait for the next message from the server
    response = wait_full_message()
    
    # Adds padding and forwards response to browser
    message = response + (BUFFER_SIZE - len(response)) * ' '
    conn.send(message.encode())


######################

# Clear clipboard
pyperclip.copy('')

# Initial setup 
find_coords()

# Wait for connections to proxy server
start()
