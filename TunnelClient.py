import cv2, pyautogui, time, pyperclip, os, base64, socket

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


def resize():
    '''Resize the WhatsApp window to make it easier to find the newest message coords easier'''
    
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
    method = cv2.TM_SQDIFF_NORMED
    small_image = cv2.imread('./assets/textbox.png')
    large_image = cv2.imread('./assets/ss.png')
    result = cv2.matchTemplate(small_image, large_image, method)
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)
    
    # Set global variables
    text_box_x, text_box_y = mnLoc


def find_new_message():
    '''Finds the spot we can triple click to copy the newest message'''
   
   # Use our globals
    global new_message_x
    global new_message_y

    # Get spot coords
    method = cv2.TM_SQDIFF_NORMED
    small_image = cv2.imread('./assets/new_message.png')
    large_image = cv2.imread('./assets/ss.png')
    result = cv2.matchTemplate(small_image, large_image, method)
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)
    
    # Set globals
    new_message_x, new_message_y = mnLoc


def write_message(message):
    '''Writes a message to WhatsApp'''

    # Click on the text box
    pyautogui.click(text_box_x,text_box_y)
    
    # Base64encode message and append a * so receiver knows when we're done
    b64message = base64.b64encode(message) + '*'.encode()
    
    # Send the messages in 844 character chunks
    while(len(b64message.decode("utf-8")) > 844):
    
        # make curr_chunk string the first 844 characters of b64message
        curr_chunk = b64message[:844]
        
        # Remove the characters in the b64message string
        b64message = b64message[844:]
        
        # write the message in the text box
        pyautogui.write(curr_chunk.decode())

        # Send the message
        pyautogui.press('enter')
        time.sleep(delay)
        
        # Wait for an ack before sending next chunk
        wait_ack()

    # write the message to the box
    pyautogui.write(b64message.decode())
    
    # click send
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
            # Checks if the pixel in the newest message is green (self), grey (server), black (ACK from either party)
            color = pyautogui.pixel((new_message_x + 90), (new_message_y - 30))
            
            # Green message bubble, sent from self
            if color == green:
                return "Self"
            
            # Grey message bubble sent from server
            elif color == grey:
                return "Server"
                
            # Black, background color, this means the message is short (has to be an ack)
            elif color == black:
                return "Ack"
                
        # For when pyautogui breaks
        except:
            pass


def read_message():
    '''Reads and returns the newest message not from self'''
    
    # Check who sent the most recent message
    sender = most_recent_sender()

    # Don't care to read acks or self messages
    if sender == "Self":
        return None
    elif sender == "Ack":
        return None

    # Highlight and copy new message
    highlight_new_message()
    pyautogui.hotkey('ctrl', 'c')
    pyautogui.press('esc')
    
    # Return message from clipboard
    new_message = pyperclip.paste()
    return new_message


def highlight_new_message():
    '''Highlights the new message'''
    pyautogui.click(new_message_x -11, new_message_y - 30)
    pyautogui.click(new_message_x -11, new_message_y - 30)
    pyautogui.click(new_message_x -11, new_message_y - 30)


def wait_full_message():
    '''Waits for the next full message to come in, ACKs and decodes as necessary'''

    # Attempt to read a message
    message = read_message()

    # If no new message available try every DELAY seconds
    while message is None or len(message) < 1:
        time.sleep(delay)
        message = read_message()

    # If it's not a full message ([-1] != '*') read it as chunks
    while message[-1] != '*':
        
        # Ack every chunk 
        write_ack()
        
        # Call read_message until new chunk is available 
        next_chunk = read_message()
        while next_chunk is None:
            time.sleep(delay)
            next_chunk = read_message()
            
        # Concat chunks
        message += next_chunk

    # Images error on utf-8 decode, easiest way to figure out if we can decode is to try
    try:
        return base64.b64decode(message[:-1]).decode()
    except:
        return base64.b64decode(message[:-1])


def wait_ack():
    '''Waits for ACK'''
    while most_recent_sender() != "Ack":
        time.sleep(delay)


def write_ack():
    '''Send ACK'''
    
    # Click on the text box
    pyautogui.click(text_box_x,text_box_y)
    
    # Write ACK
    pyautogui.write("Ack")
    
    # click send
    pyautogui.press('enter')
    time.sleep(delay)


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
    response = wait_full_message()
    
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

# Wait for connections to proxy server
start()
