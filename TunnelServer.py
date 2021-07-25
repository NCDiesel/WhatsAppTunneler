import cv2
import pyautogui
import time
import pyperclip
import os
import hashlib
import base64


### Notes ###
# pip install opencv-python, pyautogui, pyperclip, hashlib
# IMPORTANT set chat background to black, uncheck "Add whatsapp doodles"

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

### Runs on startup to find essential GUI object coordinates ###
def find_coords():
    # Take the screenshot to look for coords in
    pyautogui.screenshot('./assets/ss.png')

    # Resize the WhatsApp window
    resize()
    #os.remove('./assets/ss.png')
    pyautogui.screenshot('./assets/ss.png')

    # Find coords of gui objects
    find_new_message()
    find_text_box()

    # Remove screenshot
    #os.remove('assets\ss.png')

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

    #If a new message was copied
    if hashlib.md5(pyperclip.paste().encode('utf-8')).digest() != cliphash:
        cliphash = hashlib.md5(pyperclip.paste().encode('utf-8')).digest()
        return pyperclip.paste()

### Wait for other side to ack ###
def wait_ack():
    while read_message() != "Ack":
        time.sleep(.05)


#######################################################################################
def writeMessage(message):
    # Base64encode message
    b64message = base64.b64encode(message.encode('utf-8'))
    # append a * so receiver knows when we're done
    b64message = base64.b64encode(b64message + '*'.encode('utf-8'))
    # Send the messages in 844 character chunks
    while(message > 844):
        # click on the message box
        # make ToSend string the first 844 characters of b64message
        ToSend = b64message[:844]
        # Remove the characters in the ToSend string
        b64message = b64message[845:]
        # write the message in the text box
        pyautogui.write(ToSend)

    # write the message to the box
    pyautogui.write(b64message)
    # click send
    pyautogui.press('enter')
# Initial setup
find_coords()
print(text_box_x)
print(text_box_y)
message = "Test"
pyautogui.moveTo(text_box_x,text_box_y)
pyautogui.click()
time.sleep(3)
pyautogui.write('Hello')
pyautogui.press('enter')
#writeMessage(message)
