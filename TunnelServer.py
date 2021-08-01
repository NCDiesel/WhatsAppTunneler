import cv2, pyautogui, time, pyperclip, os, hashlib, base64, socket

'''Notes'''
# pip install opencv-python, pyautogui, pyperclip, hashlib
# IMPORTANT set chat background to black, uncheck "Add whatsapp doodles"
# Decoding and cutting the '*' will be handled by the function that calls read_message()

'''Later Problems'''
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
HOST = "192.168.1.213"
PORT = 8080


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
    pyautogui.press('end')


def find_text_box():
    '''Finds the coordinates of the textbox to write messages'''

    global text_box_x
    global text_box_y

    method = cv2.TM_SQDIFF_NORMED
    small_image = cv2.imread('./assets/textbox.png')
    large_image = cv2.imread('./assets/ss.png')
    result = cv2.matchTemplate(small_image, large_image, method)
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)
    text_box_x, text_box_y = mnLoc


def find_new_message():
    '''Finds the spot we can triple click to copy the newest message'''

    global new_message_x
    global new_message_y

    method = cv2.TM_SQDIFF_NORMED
    small_image = cv2.imread('./assets/new_message.png')
    large_image = cv2.imread('./assets/ss.png')
    result = cv2.matchTemplate(small_image, large_image, method)
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)
    new_message_x, new_message_y = mnLoc


def write_message(message):
    '''Writes a message to WhatsApp'''

    pyautogui.click(text_box_x,text_box_y)
    # Base64 encode message and append a * so receiver knows when we're done
    b64message = base64.b64encode(message.encode('utf-8')) + '*'.encode('utf-8')
    # Send the messages in 844 character chunks
    while(len(b64message.decode("utf-8")) > 844):
        curr_chunk = b64message[:844]
        b64message = b64message[845:]
        pyautogui.write(curr_chunk)
        wait_ack()

    pyautogui.write(b64message.decode("utf-8"))
    pyautogui.press('enter')
    

def read_message():
    '''Reads and returns the newest message not from self'''

    global cliphash

    highlight_new_message()
    
    # Attempt to copy
    pyautogui.hotkey('ctrl', 'c')
    
    # Escape in case we highlighted our own message
    pyautogui.press('esc')

    new_message = pyperclip.paste()
    if new_message == "Ack":
        return new_message

    new_msg_hash = hashlib.md5(pyperclip.paste().encode('utf-8')).digest()
    if new_msg_hash != cliphash:
        cliphash = new_msg_hash
        return new_message
    else:
        return None

def highlight_new_message():
    '''Highlights the new message'''

    pyautogui.click(new_message_x, new_message_y - 30)
    pyautogui.click(new_message_x, new_message_y - 30)
    pyautogui.click(new_message_x, new_message_y - 30) 


def wait_full_message():
    '''Waits for the next full message to come in, ACKs and decodes as necessary'''

    message = read_message()

    while message is None:
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


def wait_ack():
    '''Waits for ACK'''
    while read_message() != "Ack":
        time.sleep(delay)


def write_ack():
    '''Send ACK'''
    pyautogui.click(text_box_x,text_box_y)
    pyautogui.write("Ack")
    pyautogui.press('enter')


def squid_tunnel(request):
    '''Handle communications with squid'''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(request.encode('utf-8'))
        rec = s.recv(1024)
    return response


def serve():
    '''Take requests send responses forever'''
    while(True):
        request = wait_full_message()
        response = squid_tunnel(request)
        write_message(response)


# ---------------------------------------------------------- #

# Initial setup 
find_coords()

# Be a server
serve()