import socket
import cv2
import urllib
import numpy as np
import pickle
import struct
import argparse


parser = argparse.ArgumentParser(description='local_cv')

parser.add_argument('--stream-host', dest='stream_host', action="store", default='127.0.0.1')
parser.add_argument('--stream-port', dest='stream_port', action="store", default='5050')
parser.add_argument('--server-host', dest='server_host', action="store", default='127.0.0.1')
parser.add_argument('--server-port', dest='server_port', action="store", default='5052')
results = parser.parse_args()


server_host, server_port = results.server_host, int(results.server_port)
stream_host, stream_port = results.stream_host, int(results.stream_port)

connection_established = False
server = None


def connect():
    global connection_established, server
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((server_host, server_port))
        connection_established = True
    except socket.error:
        print("[ERROR]: Could not established socket connection!")
        connection_established = False


def capture(send=False, imshow=False):
    stream = urllib.urlopen('http://'+stream_host+':'+str(stream_port)+'/video.mpjpeg')
    bytes = ''
    while True:
        bytes += stream.read(1024)
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes[a:b+2]
            bytes = bytes[b+2:]
            i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            if imshow:
                cv2.imshow('remote_frame', i)
            
            if send and connection_established:
                try:
                    data = pickle.dumps(i)
                    server.sendall(struct.pack("L", len(data)) + data)
                except socket.error:
                    print("[ERROR]: Could not send data to the client!")
                    
            if cv2.waitKey(1) == 27:
                if connection_established:
                    try:
                        server.close()
                    except socket.error:
                        print("[ERROR]: Could not close the socket!")
                exit(0)

connect()
capture(send=True, imshow=False)