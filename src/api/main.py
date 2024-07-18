import io
import os
import serial
import time
import logging, logging.handlers

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

from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class MDBSetupResponse:
    feature_level: str
    country_currency_code: str
    coin_scaling_factor: str
    decimal_places: str
    coin_type_routing: List[int]
    coin_type_credit: List[int]

    @classmethod
    def from_hex(cls, hex_str: str):
        # Unpack the hex string into the fields
        feature_level = int(hex_str[0:2], 16)
        country_currency_code = int(hex_str[2:6],16)
        coin_scaling_factor = int(hex_str[6:8],16)
        decimal_places = int(hex_str[8:10],16)
        coin_type_routing = [key for key,value  in enumerate(reversed(f"{int(hex_str[10:14],16):b}")) if value == "1"]

        coin_type_credit = [int(hex_str[i:i+2], 16) for i in range(14, len(hex_str), 2)]
        
        return cls(feature_level, country_currency_code, coin_scaling_factor, 
                   decimal_places, coin_type_routing, coin_type_credit)


class VMCDiagnosticStatus:

    def __init__(self, main_code, sub_code):
        self.main_code = main_code
        self.sub_code = sub_code

    
    DIAGNOSTIC_CODES = {
        "01": {"00": "Powering up - Changer powering up / initialization"},
        "02": {"00": "Powering down - Changer powering down"},
        "03": {"00": "OK - Changer fully operational and ready to accept coins"},
        "04": {"00": "Keypad shifted - MODE key pressed and held..."},
        "05": {"10": "Manual Fill / Payout active", 
               "20": "New Inventory Information Available"},
        "06": {"00": "Inhibited by VMC - All coin acceptance inhibited..."},
        "10": {"00": "General changer error - Non specific error",
               "01": "Check sum error #1",
               "02": "Check sum error #2",
               "03": "Low line voltage detected"},
        "11": {"00": "Discriminator module error - Non specific...",
               "10": "Flight deck open",
               "11": "Escrow Return stuck open",
               "30": "Coin jam in sensor",
               # ... more errors from 11 here
               },
        "12": {"00": "Accept gate module error - Non specific...",
               "30": "Coins entered gate, but did not exit",
               # ... more errors from 12 here
               },
        "13": {"00": "Separator module error - Non specific...",
               "10": "Sort sensor error",
               # ... more errors from 13 here
               },
        "14": {"00": "Dispenser module error - Non specific..."},
        "15": {"00": "Coin Cassette / tube module error - Non specific...",
               "02": "Cassette removed",
               "03": "Cash box sensor error",
               "04": "Sunlight on tube sensors"},
        # ... more codes as necessary
    }

    @classmethod
    def from_hex(cls, hex_str: str):
        # Assume Z1 and Z2 are always 2 bytes each
        z1 = hex_str[:2]
        z2 = hex_str[2:4]
        return cls(z1, z2)

   
    def __str__(self) -> str:
        main_code_info = self.DIAGNOSTIC_CODES.get(self.main_code, {})
        return main_code_info.get(self.sub_code, "Unknown diagnostic code")
  
class DiagnosticResponse:
    def __init__(self, hex_string, logger : logging.Logger = None):
        self.messages = []
        for i in range(0,len(hex_string),4):
            diag_message = VMCDiagnosticStatus.from_hex(hex_string[i:i+4])
            self.messages.append(diag_message)
            if logger != None:
                logger.debug(f"Diag response: {diag_message.main_code}/{diag_message.sub_code}: {diag_message}")


    def __str__(self):
        result = ""
        for s in self.messages:
            result += str(s) + "\n"
        return result
    def __contains__(self, codes):
        if len(codes) != 2:
            return False
        for status in self.messages:
            if status.main_code == codes[0] and status.sub_code == codes[1]:
                return True
        return False
    
class StatusResponse:
    MESSAGES = {
        "00000001": "Escrow request - An escrow lever activation has been detected.",
        "00000010": "Changer Payout Busy - The changer is busy activating payout devices.",
        "00000011": "No Credit - A coin was validated but did not get to the place in the system when credit is given.",
        "00000100": "Defective Tube Sensor - The changer has detected one of the tube sensors behaving abnormally.",
        "00000101": "Double Arrival - Two coins were detected too close together to validate either one.",
        "00000110": "Acceptor Unplugged - The changer has detected that the acceptor has been removed.",
        "00000111": "Tube Jam - A tube payout attempt has resulted in a jammed condition.",
        "00001000": "ROM checksum error - The changers internal checksum does not match the calculated checksum.",
        "00001001": "Coin Routing Error - A coin has been validated, but did not follow the intended routing.",
        "00001010": "Changer Busy - The changer is busy and cannot answer a detailed command right now.",
        "00001011": "Changer was Reset - The changer has detected a Reset condition and has returned to its power-on idle condition.",
        "00001100": "Coin Jam - A coin(s) has jammed in the acceptance path.",
        "00001101": "Possible Credited Coin Removal – There has been an attempt to remove a credited coin."
    }

    def __init__(self, code):
        self.code = code

    def __str__(self):
        return self.MESSAGES.get(self.code, "Unknown status")

class SlugResponse:
    def __init__(self, count):
        self.count = count

    def __str__(self):
        return f"Slug detected, there has been {self.count} slugs since the last activity."

class CoinsDepositedResponse:
    ROUTING = {
        "00": "CASH BOX",
        "01": "TUBES",
        "10": "NOT USED",
        "11": "REJECT"
    }

    def __init__(self, routing, coin_type, coins_in_tube):
        self.routing = routing
        self.coin_type = coin_type
        self.coins_in_tube = coins_in_tube

    def __str__(self):
        return (f"Coins Deposited - Routing: {self.ROUTING[self.routing]}, "
                f"Coin Type: {self.coin_type}, Coins in Tube: {self.coins_in_tube}")

class CoinsDispensedResponse:
    def __init__(self, num_coins_dispensed, coin_type, coins_in_tube):
        self.num_coins_dispensed = num_coins_dispensed
        self.coin_type = coin_type
        self.coins_in_tube = coins_in_tube

    def __str__(self):
        return (f"Coins Dispensed Manually - Number: {self.num_coins_dispensed}, "
                f"Coin Type: {self.coin_type}, Coins in Tube: {self.coins_in_tube}")

class VMCPollResponseParser:
    @staticmethod
    def parse_single_response(bin_string):
        # Slug
        if bin_string.startswith("001"):
            slug_count = int(bin_string[3:], 2)
            return SlugResponse(slug_count)

        # Status
        if bin_string[:8] in StatusResponse.MESSAGES:
            return StatusResponse(bin_string[:8])

        # Coins Deposited
        if bin_string.startswith("01"):
            routing = bin_string[2:4]
            coin_type = int(bin_string[4:8], 2)
            coins_in_tube = int(bin_string[8:16], 2)
            return CoinsDepositedResponse(routing, coin_type, coins_in_tube)

        # Coins Dispensed Manually
        if bin_string.startswith("1"):
            num_coins_dispensed = int(bin_string[1:4], 2)
            coin_type = int(bin_string[4:8], 2)
            coins_in_tube = int(bin_string[8:16], 2)
            return CoinsDispensedResponse(num_coins_dispensed, coin_type, coins_in_tube)

        return None

    @staticmethod
    def parse(hex_string):
        if hex_string == "":
            return []
        if hex_string == "ACK": # Nothing's happening
            return []
        # Convert the entire hex string to a binary string
        bin_string = format(int(hex_string, 16), '0' + str(8*len(hex_string)//2) + 'b')
        
        responses = []
        i = 0
        while i < len(bin_string):
            # Determine response type
            if bin_string[i:i+3] == "001":  # Slug
                responses.append(VMCPollResponseParser.parse_single_response(bin_string[i:i+8]))
                i += 8
            elif bin_string[i:i+8] in StatusResponse.MESSAGES:  # Status
                responses.append(VMCPollResponseParser.parse_single_response(bin_string[i:i+8]))
                i += 8
            elif bin_string[i:i+2] in ["00", "01", "10", "11"] or bin_string[i] == "1":  # A 2-byte response
                responses.append(VMCPollResponseParser.parse_single_response(bin_string[i:i+16]))
                i += 16
            else:
                # Handle unexpected patterns, can be modified as per requirement
                i += 8
        
        return responses
    
def setup_validator(sc: SerialComm):
    print("Reading version information")
    sc.write("V")
    print(sc.read())

    print("Setting master mode")
    sc.write("M,1")
    print(sc.read())

    print("Resetting coin acceptor")
    sc.write("R,08")
    reset_response = sc.read()
    while reset_response != "p,ACK":
        print("No response, trying again")
        print("Resetting coin acceptor")
        sc.write("R,08")
        reset_response = sc.read()
        time.sleep(1)
    
    print("Setup")
    sc.write("R,09")
    setup_result = sc.read()
    setup_response = MDBSetupResponse.from_hex(setup_result[2:])
    print(setup_response)

    print("Read tube status")
    sc.write("R,0A")
    print(sc.read())

    print("Enable coins")
    sc.write("R,0C,FFFFFFFF")
    print(sc.read())
    return setup_response

serial_singleton = None
def get_serial(logger):
    global serial_singleton
    if not serial_singleton:
        serial_singleton = SerialComm(logger = logger)
    return serial_singleton

def dispense(value, number):
    sc = get_serial(get_logger())
    coin_index_to_dispense = value
    i =  16 + coin_index_to_dispense
    sc.write(f"R,0D,{i:X}")
    dispense_response = sc.read()
    return dispense_response

def main():
    
    dipense_counter = 0
    logger = get_logger()

    last_diag_status = ""
    print("MDB Tester")
    sc = get_serial(logger)
    setup_response = setup_validator(sc)
    dispese_indexes = setup_response.coin_type_routing
    
    print("Polling Started")
    try:
        
        while True:
            sc.write("R,0B")
            poll_response = sc.read()
            poll_responses_parsed = VMCPollResponseParser.parse(poll_response[2:])
            for response in poll_responses_parsed:
                if isinstance(response, CoinsDepositedResponse):
                    if response.routing =="01":
                        coin_index_to_dispense = dispese_indexes[dipense_counter % len(dispese_indexes)]
                        i = 16 + coin_index_to_dispense
                        sc.write(f"R,0D,{i:X}")
                        dispense_response = sc.read()
                        dipense_counter += 1
                print(response)

            sc.write("R,0F,05")
            diag_res = sc.read()
            status = DiagnosticResponse(diag_res[2:],logger=logger)
            if str(status) != last_diag_status:
                print(status)
                last_diag_status = str(status)

            if ("06","00") in status:
                print("Re-enabling validator")
                sc.write("R,0C,FFFFFFFF")
                print(sc.read())
            time.sleep(1)
    except KeyboardInterrupt:
        print("Terminating")
        sc.close()

def get_logger():
    logger = logging.getLogger("MDB")
    return logger
    os.makedirs("log", exist_ok = True)
    handler = logging.handlers.TimedRotatingFileHandler("/var/log/mdb_comm_log", when="midnight", interval=1, backupCount=0)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.level=logging.DEBUG
    return logger
    
if __name__ == "__main__":
    main()
    

    