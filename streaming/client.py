import socket
import cv2
import pickle
import struct
import threading


class CameraClient:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__running = False
        self.__client_socket = socket.socket(socket.AF_INET,
                                             socket.SOCK_STREAM)
        self.__camera = cv2.VideoCapture(0)

    def __cleanup(self):
        self.__camera.release()
        cv2.destroyAllWindows()

    def __get_frame(self):
        ret, frame = self.__camera.read()
        return frame

    def __client_streaming(self):
        self.__client_socket.connect((self.__host, self.__port))
        while self.__running:
            frame = self.__get_frame()
            result, frame = cv2.imencode('.jpg', frame)
            data = pickle.dumps(frame, 0)
            size = len(data)

            try:
                self.__client_socket.sendall(struct.pack('>L', size) + data)
            except ConnectionResetError:
                self.__running = False
            except ConnectionAbortedError:
                self.__running = False
            except BrokenPipeError:
                self.__running = False
        self.__cleanup()

    def start_stream(self):
        if self.__running:
            print("Client is already streaming!")
        else:
            self.__running = True
            client_thread = threading.Thread(target=self.__client_streaming)
            client_thread.start()

    def stop_stream(self):
        if self.__running:
            self.__running = False
        else:
            print("Client not streaming!")


if __name__ == '__main__':
    client = CameraClient("192.168.1.127", 9999)
    client.start_stream()
