import io
import logging
import time

import serial


class SerialComm:
    def __init__(self,logger : logging.Logger = None):
        self.logger = logger
        self.ser = serial.Serial(port="/dev/serial0", baudrate=115200, timeout=0.1)
        if not self.ser.isOpen():
            self.ser.open()
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser,self.ser))
    
    def write(self, message:str):
        if not self.ser.isOpen():
            self.ser.open()
        self.logger.debug(f"Writing {message}")
        self.sio.write(message+"\n")
        self.sio.flush()
        

    def read(self, timeout_in_ms:int = 5):
        for i in range(timeout_in_ms):
            buffer = self.sio.readline()
            if len(buffer) > 0:
                break
            time.sleep(0.1)
        if "\n" in buffer:
            buffer = buffer[:-1]
        if(len(buffer) == 0):
            self.logger.debug(f"Didn't receive a response in {timeout_in_ms} ms")
        else:
            self.logger.debug(f"Received {buffer}")
        return buffer
    
    def close(self):
        self.ser.close()
