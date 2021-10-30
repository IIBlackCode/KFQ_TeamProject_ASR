# IMAGE 수신 모듈

from ctypes import sizeof
import socket
import cv2
import time
from datetime import datetime
import numpy
import base64
import threading
from select import select
import sys
from time import ctime

#WebCamera Version Module import
from .TurtlebotCamera.ssdNet import ssdNet
from .TurtlebotCamera.gesture_recognition import Gesture_recognition
from .TurtlebotCamera.MaskDetection import maskDetection

stringData = None
BUFSIZE = 1024


class ServerSocket:
    
    def __init__(self, ip, port):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.socketOpen()
        self.receiveThread = threading.Thread(target=self.receiveImages)
        self.receiveThread.start()

    def socketClose(self):
        self.sock.close()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is close')
        self.sock = None

    def socketOpen(self):
        # 1. Socket 객체 생성
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

        # 2. 서버정보 바인딩
        self.sock.bind((self.TCP_IP, self.TCP_PORT))

        # 3. 요청 기다림
        self.sock.listen(1)

        connection_list = [self.sock]
        print('==============================================')
        print('이미지 수신 시작 %s ' % str(self.TCP_PORT))
        print('==============================================')

        while connection_list:
            print('[INFO] 요청 대기중')
            # select 로 요청을 받고, 10초마다 블럭킹을 해제하도록 함
            read_socket, write_socket, error_socket = select(connection_list, [], [], 10)

            for sock in read_socket:
                # NEW Socket
                if sock == self.sock:
                    # clientSocket, addr_info = self.sock.accept()
                    self.conn, self.addr = self.sock.accept()
                    connection_list.append(self.conn)
                    print('[INFO][%s] 클라이언트(%s)가 새롭게 연결 되었습니다.' % (ctime(), self.addr[0]))

                    print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is open')
                    try:
                        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is connected with client')
                    except Exception as e:
                        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is disconnected with client')
    
    def receiveImages(self, model):
        global stringData
        try:
            while True:
                length = self.recvall(self.conn, 64)
                length1 = length.decode('utf-8')
                stringData = self.recvall(self.conn, int(length1))
                # stime = self.recvall(self.conn, 64)
                # print('send time: ' + stime.decode('utf-8'))
                # now = time.localtime()
                # print('receive time: ' + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'))
                data = numpy.frombuffer(base64.b64decode(stringData), numpy.uint8)
                
                if model == "webcam":
                    pass
                elif model == "ObjectDetection":
                    image = ssdNet(data)
                elif model == "gesture-recognition":
                    image = Gesture_recognition()
                    image = image.gesture_recognition(data)
                elif model == "MaskDetection":
                    image = maskDetection(data)
                else:
                    pass
                
                # decimg = cv2.imdecode(data, 1)
                # _, jpeg = cv2.imencode('.jpg', data)
                # cv2.imshow("image", decimg)
                # cv2.waitKey(1)
                return data.tobytes()
        except Exception as e:
            print(e)
            self.socketClose()
            cv2.destroyAllWindows()
            self.socketOpen()
            self.receiveThread = threading.Thread(target=self.receiveImages)
            self.receiveThread.start()

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

# def main():
#     server = ServerSocket('192.168.0.212', 9090)

# if __name__ == "__main__":
#     main()