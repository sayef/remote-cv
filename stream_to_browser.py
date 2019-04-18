# python python_video_streamer.py
# From browser:
# http://127.0.0.1:9000/cam.html or
# http://127.0.0.1:9000/cam.mjpg
    
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import socket
import time
from SocketServer import ThreadingMixIn


class StreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print self.path
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            while True:
                try:
                    # get frame from any message queue, i.e RabbitMQ, ROS usb_cam, ZMQ, Kafka etc
                    # or save the frames in disk using opencv: cv2.imwrite('temp.jpg', frame)
                    # and read from here
                    img = open('temp.jpg', 'rb').read()

                    self.wfile.write("--jpgboundary\r\n")
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', str(len(img)))
                    self.end_headers()
                    self.wfile.write(bytearray(img))
                    self.wfile.write('\r\n')
                    time.sleep(0.2)
                except KeyboardInterrupt:
                    break
            return
        if self.path.endswith('.html') or self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>')
            self.wfile.write('<img src=":9000/cam.mjpg"/>')
            self.wfile.write('</body></html>')
            return

    def handle(self):
        try:
            BaseHTTPRequestHandler.handle(self)
        except socket.error:
            pass

    def finish(self):
        try:
            if not self.wfile.closed:
                self.wfile.flush()
            self.wfile.close()
            self.rfile.close()
        except socket.error:
            pass
        self.rfile.close()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def main():
    global server
    try:
        server = ThreadedHTTPServer(('0.0.0.0', 9000), StreamHandler)
        print "Server started ..."
        server.serve_forever()
    except KeyboardInterrupt:
        server.handle()
        server.finish()
        server.socket.close()
        exit(0)


if __name__ == '__main__':
    main()
