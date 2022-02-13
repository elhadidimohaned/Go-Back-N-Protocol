import socket
import os
import select
import threading
import string
import json
import random

MAX_SEQ = 3
networkEnable = None
timeout = 0
missedFrame = 100
networkEnable=0

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))

timerOfFrame = []

def increment(k):
    if k < MAX_SEQ:
        k = k + 1
    else:
        k = 0
    return k

def wait_for_event():

    global timeout
    ready_sockets, _, _ = select.select ([s], [], [], 0)

    if ready_sockets:
        return 1
    elif timeout:
        timeout=0
        return 2
    elif networkEnable:
        return 3
    else:
        return 0

def from_network_layer():
    packet = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return packet

def to_network_layer(packet):
    packetq = ""
    
def to_physical_layer(r):
    s.send(bytes(json.dumps(r),"utf-8"))

def from_physical_layer():
    msg = s.recv(56)
    r = json.loads(msg.decode("utf-8"))
    return r
        
def enable_network_layer():
    global networkEnable 
    networkEnable = 1

def disable_network_layer():
    global networkEnable
    networkEnable = 0

def start_timer(seq_frame):
    timer = threading.Timer(5.0, timer_callBack, [seq_frame]) 
    timerOfFrame[seq_frame]["timer"] = timer
    timer.start()

def stop_timer(seq_frame):
    timerOfFrame[seq_frame]["timer"].cancel()

def delay():
    for j in range(100000):
        t = None

def timer_callBack(frameNum): 
    print(f"\n Frame {frameNum} timeout") 
    missedFrame = frameNum
    global timeout
    timeout=1

def between(a, b, c):
    if (((a <= b) and (b < c)) or ((c < a) and (a <= b)) or ((b <=c) and (c < a))):
        return True 
    else:
        return False

    
def send_data( NRframe,expectedFrame,buffer):

    s = {"seqNum":NRframe, "ack": (expectedFrame + MAX_SEQ) % (MAX_SEQ + 1), "info": buffer[NRframe],"kind":"data"}
    to_physical_layer(s)
    start_timer(NRframe)
    print(f"{s}")
    delay()


if __name__ == "__main__":

    buffer=["","","",""] 

    enable_network_layer() 
    expectedACK = 0 
    next_frame_sending = 0 
    expectedFrame = 0 
    nbuffered = 0     

    for i in range(MAX_SEQ+1):
        timerOfFrame.append({"seqNum": i, "timer":None})
    while True:
        event = wait_for_event()
        if event == 3:
            buffer[next_frame_sending] = from_network_layer() 
            nbuffered = nbuffered + 1
            print(f"\nFrame {next_frame_sending} sent")
            send_data(next_frame_sending, expectedFrame, buffer) 
            next_frame_sending = increment(next_frame_sending)  

        elif event == 1:
            r=from_physical_layer()   
            if r["seqNum"] == expectedFrame:   
                to_network_layer(r["info"]) 
                expectedFrame=increment(expectedFrame) 
                    
            while between(expectedACK, r["ack"], next_frame_sending):
                nbuffered = nbuffered - 1 
                stop_timer(expectedACK)  
                print(f"\nframe {r['ack']} acked")
                expectedACK = increment(expectedACK) 
                
        elif event == 2:
            next_frame_sending = expectedACK  
            temp = next_frame_sending
            for j in range(nbuffered):
                stop_timer(temp)
                temp = increment(temp)
            for i in range(nbuffered):
                print(f"\nframe {next_frame_sending} retransmitted")
                send_data(next_frame_sending, expectedFrame, buffer)
                next_frame_sending = increment(next_frame_sending) 

        if (nbuffered <= MAX_SEQ):
            enable_network_layer()
        else:
            disable_network_layer()      