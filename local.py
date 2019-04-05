import socket
import sys
import cv2
import pickle
import struct
import argparse
import subprocess
from threading import Thread

parser = argparse.ArgumentParser(description='remote_cv')

parser.add_argument('--stream-host', dest='stream_host', action="store", default='127.0.0.1')
parser.add_argument('--stream-port', dest='stream_port', action="store", default='5050')
parser.add_argument('--server-host', dest='server_host', action="store", required=True)
parser.add_argument('--server-port', dest='server_port', action="store", required=True)
results = parser.parse_args()

stream_args = {
    'fps': '30',
    'width': '320',
    'height': '240',
    'host': results.stream_host,
    'port': results.stream_port
}

command = "cvlc -vvv v4l2:// --sout '#transcode{fps=$fps,vcodec=mjpg,vb=2000,width=$width,height=$height,venc=ffmpeg}:duplicate{dst=standard{access=http,mux=mpjpeg,dst=$host:$port/video.mpjpeg}'"
client = None

class Command(object):
    '''
    Enables to run subprocess commands in a different thread
    with TIMEOUT option!
    Based on jcollado's solution:
    http://stackoverflow.com/questions/1191374/subprocess-with-timeout/4825933#4825933
    '''
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout=0, **kwargs):
        def target(**kwargs):
            self.process = subprocess.Popen(self.cmd, **kwargs)
            self.process.communicate()

        thread = Thread(target=target, kwargs=kwargs)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()

        return self.process


def stream():
    global command
    for key, val in stream_args.items():
        command = command.replace('$' + key, val)
    print command

    command = Command(command)
    return command.run(timeout=1, shell=True, stdout=sys.stdout, stderr=sys.stderr)


def connect():
    '''
    Creates client socket to receive data from server socket
    Needs to established before server starts to send data
    :return: 
    '''

    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind((results.server_host, int(results.server_port)))
    client.listen(10)


def receive():
    '''
    Receives data after successful socket connection to server
    :return: 
    '''
    global client
    print('Receiving...\n')         
    conn, addr = client.accept()

    data = ""
    payload_size = struct.calcsize("L")
    while True:
        while len(data) < payload_size:
            _data = conn.recv(4096)
            if len(_data) == 0:
                conn, addr = client.accept()
            else:
                data += _data
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]

        msg_size = struct.unpack("L", packed_msg_size)[0]
        while len(data) < msg_size:
            data += conn.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data)
        cv2.imshow('local_frame', frame)

        key = cv2.waitKey(10)
        if (key == 27) or (key == 113):
            break


def close():
    global client
    client.close()


process = None
try:
    process = stream()
    connect()
    receive()
except KeyboardInterrupt:
    print('Exiting...')
except OSError as e:
    print(e)
    exit(1)
finally:
    close()
    if process is not None:
        process.kill()
