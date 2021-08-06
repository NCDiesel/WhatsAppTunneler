import pyautogui, time, pyperclip, os, base64, socket, numpy

"""
NOTES
pip install opencv-python, pyautogui, pyperclip
IMPORTANT set chat background to black, uncheck "Add whatsapp doodles"
"""

# Globals
new_message_x = 0
new_message_y = 0
text_box_x = 0
text_box_y = 0
delay = .6
HOST = ''
PORT = 44455
BUFFER_SIZE = 12048


def find_coords():
    '''Runs on startup to find essential GUI object coordinates'''

    # Resize the WhatsApp window
    resize()
    
    # Find coords of gui objects
    find_new_message()
    find_text_box()


def resize():
    '''Resize the WhatsApp window to make it easier to find the newest message coords easier'''
    
    # Get coords to change window size
    X, Y, z, z = pyautogui.locateOnScreen('./assets/resize.png')
    
    # Drag the window all the way to the left
    pyautogui.moveTo(X + 50, Y)
    pyautogui.dragTo(0, Y)
    
    # Spam pagedown to go to the bottom of chat after window resize
    pyautogui.press('pagedown')
    pyautogui.press('pagedown')
    pyautogui.press('pagedown')
    pyautogui.press('pagedown')


def find_text_box():
    '''Finds the coordinates of the textbox to write messages'''
   
    # Use our globals 
    global text_box_x
    global text_box_y

    # Find the coords of the textbox asset
    text_box_x, text_box_y, z, z = pyautogui.locateOnScreen('./assets/textbox.png')


def find_new_message():
    '''Finds the spot we can triple click to copy the newest message'''
   
   # Use our globals
    global new_message_x
    global new_message_y

    # Get spot coords
    new_message_x, new_message_y, z, z = pyautogui.locateOnScreen('./assets/new_message.png')

    # Convert numpy to into
    new_message_x = numpy.int64(new_message_x).item()
    new_message_y = numpy.int64(new_message_y).item()
    

def read_more():
    ''' Annoying function to click all possible locations of the read more button '''

    # Background color, boolean, x-coordinates
    black = (10, 12, 13)
    done = False
    xvals = [65, 150, 200]
    
    # Click all possible read more button locations until message doesn't get longer
    while not done:
        for val in xvals:
            pyautogui.click(new_message_x + val, new_message_y - 45)
            pyautogui.click(new_message_x + val, new_message_y - 65)

        # If read more button is pressed the background color won't be present here
        tryloop = True
        while tryloop:
            try:
                if pyautogui.pixel(new_message_x + 10, new_message_y - 20) == black:
                    done = True
                else:
                    pyautogui.press('end')
                tryloop = False
            except:
                pass


def write_message(message):
    '''Writes a message to WhatsApp'''

    # Click on the text box
    pyautogui.click(text_box_x,text_box_y)
    
    # Base64encode message and append a * so receiver knows when we're done
    b64message = base64.b64encode(message)
    pyperclip.copy(b64message.decode())
    
    # Paste message into box
    pyautogui.hotkey('ctrl', 'v')    

    # Send the message
    pyautogui.press('enter')
    time.sleep(delay)


def most_recent_sender():
    '''Reads a pixel color of the newest message to determine what type of message it is'''
    # R, G, B Colors
    green = (5, 97, 98)
    grey = (38, 45, 49)
    black = (10, 12, 13)
    
    # Try until it works because the pyautogui pixel function has a 50-50 chance of erroring
    while True:
        try:
            # Checks if the pixel in the newest message is green (self), grey (server), black not a real message ignore
            color = pyautogui.pixel((new_message_x + 90), (new_message_y - 30))
            
            # Green message bubble, sent from self
            if color == green:
                return "Self"
            
            # Grey message bubble sent from server
            elif color == grey:
                return "Server"
                
            # Black, background color, this means the message is short, not a real message
            elif color == black:
                return "TooShort"
                
        # For when pyautogui breaks
        except:
            pass


def read_message():
    '''Reads and returns the newest message not from self'''
    
    # Check who sent the most recent message
    sender = most_recent_sender()

    # If no new message is available 
    while sender != "Server":
        time.sleep(delay)
        sender = most_recent_sender()

    # Fully expand message
    read_more()

    # Highlight and copy new message
    highlight_new_message()
    pyautogui.hotkey('ctrl', 'c')
    pyautogui.press('esc')
    
    # Return message from clipboard
    new_message = pyperclip.paste()

    # Images error on utf-8 decode, easiest way to figure out if we can decode is to try
    try:
        return base64.b64decode(new_message).decode()
    except:
        return base64.b64decode(new_message)


def highlight_new_message():
    '''Highlights the new message'''
    pyautogui.click(new_message_x -11, new_message_y - 30)
    pyautogui.click(new_message_x -11, new_message_y - 30)
    pyautogui.click(new_message_x -11, new_message_y - 30)


def start():
    '''Proxy functions'''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        
        while True:
            conn, addr = s.accept()
            print('Connection from ', addr)
            data = conn.recv(BUFFER_SIZE)
            #if not data:
            #    break
            garbage = ["firefox", "pocket", "mozilla.com", "mozilla.net", "telem", "push.services", "safebrow"]
            if any(x in data.decode() for x in garbage):
                continue
            tunnel_request(data, conn)


def tunnel_request(data, conn):
    '''Forwards request to server'''

    # Writes WhatsApp message
    write_message(data)
    time.sleep(.5)

    # Wait for the next message from the server
    response = read_message()
    
    # Adds padding and forwards response to browser, bytes if needed
    try:
        message = response + (BUFFER_SIZE - len(response)) * ' '
    except:
        message = response + (BUFFER_SIZE - len(response)) * b'\x00'
    
    # Encode it unless it fails to encode
    try:
        conn.send(message.encode())
    except:
        conn.send(message)
        
        
# ----------------------------------------------------------------- #

# Clear clipboard
pyperclip.copy('')

# Start delayed so you have time to minimize things
time.sleep(4)

# Initial setup 
find_coords()

# Start communications
write_message(b"A")

# Wait for connections to proxy server
start()
