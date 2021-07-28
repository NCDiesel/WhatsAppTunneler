import cv2
import pyautogui
import time
import pyperclip
import os 
import hashlib
import base64
import socket

### Notes ###
# pip install opencv-python, pyautogui, pyperclip, hashlib
# IMPORTANT set chat background to black, uncheck "Add whatsapp doodles"
# Decoding and cutting the '*' will be handled by the function that calls read_message()

### Later Problems ###
# There could be problems with multiple requests
# at once, or sending responses or requests wile
# the other side is waiting for an ack. 

# Globals
cliphash = ""
new_message_x = 0
new_message_y = 0
text_box_x = 0
text_box_y = 0
delay = .05 

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
    os.remove('assets\ss.png')

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
    pyautogui.press('end')

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
def writeMessage(message):
    # Click on the text box
    pyautogui.click(text_box_x,text_box_y)
    # Base64encode message
    # b64message = base64.b64encode(message.encode('utf-8'))
    # append a * so receiver knows when we're done
    b64message = base64.b64encode(message.encode('utf-8'))
    b64message = b64message +  '*'.encode('utf-8')
    # Send the messages in 844 character chunks
    while(len(b64message.decode("utf-8")) > 844):
        # click on the message box
        # make ToSend string the first 844 characters of b64message
        ToSend = b64message[:844]
        # Remove the characters in the ToSend string
        b64message = b64message[845:]
        # write the message in the text box
        pyautogui.write(ToSend)
        # Wait for an ack
        wait_ack()

    # write the message to the box
    pyautogui.write(b64message.decode("utf-8"))
    # click send
    pyautogui.press('enter')
    
### Attempts to read the newest message ###
### Returns: Returns newest message if not from self ###
def read_message():
    global cliphash

    # Highlight possible new message
    pyautogui.click(new_message_x, new_message_y - 30)
    pyautogui.click(new_message_x, new_message_y - 30)
    pyautogui.click(new_message_x, new_message_y - 30)
    
    # Attempt to copy
    pyautogui.hotkey('ctrl', 'c')
    
    # Escape in case we highlighted our own message
    pyautogui.press('esc')

    if pyperclip.paste() == "Ack":
        return "Ack"

    #If a new message was copied 
    if hashlib.md5(pyperclip.paste().encode('utf-8')).digest() != cliphash:
        cliphash = hashlib.md5(pyperclip.paste().encode('utf-8')).digest()
        return pyperclip.paste()
    
    # If nothing has changed
    return None

### Waits for the next full message to come in ###
### Acks and decodes as necessary ###
def wait_full_message():
    # Wait for a response from server
    initial = None
    time_wait = 0
    while initial is None:
        time.sleep(time_wait)
        initial = read_message()
        time_wait = delay

    # Wait for the rest of response if not complete (doesn't end with *)
    chunk = None
    time_wait = 0
    while initial[-1] != '*':
        write_ack()
        while chunk is None:
            time.sleep(time_wait)
            chunk = read_message()
            time_wait = delay
        initial = initial + chunk
        chunk = None
    full = initial[:-1]
    decoded = base64.b64decode(full).decode('utf-8')
    return decoded

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

### Handle communications with squid ###
def squid_stuff(request):
    # Send a request to the squid server
    # return the response from the squid server
    return response

### The main loop for our server program ###
### Take requests send responses forever ###
def serve():
    # Loop forever
    while(True):
        # 1: Wait for request from client
        request = wait_full_message()
        # 2: Forward request to squid
        # 3: Get response from squid
        response = squid_stuff(request)
        # 4: Write response to client
        write_message(response)

# Initial setup 
find_coords()

# Be a server
serve()