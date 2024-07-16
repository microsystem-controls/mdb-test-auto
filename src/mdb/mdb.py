from logging import Logger
from .serialcomm import SerialComm


class MDB:
    def __init__(self):
        self.serial = SerialComm(Logger("mdb"))
        self.serial.write("M,1")
        if self.serial.read() != "m,ACK":
            raise Exception("Failed to set master mode")

    def dispense(self, value, number):
        coin_index_to_dispense = value
        i =  16 + coin_index_to_dispense
        self.serial.write(f"R,0D,{i:X}")
        dispense_response = self.serial.read()
        return dispense_response
    
    def id(self):
        self.serial.write("R,09")
        setup_result = self.serial.read()
        self.serial.write("R,0f,00")
        info = self.serial.read()
        self.serial.write("R,09")
        setup_result = self.serial.read()
        setup_response = MDBSetupResponse.from_hex(setup_result[2:])
        
        return info, setup_response

        
    def poll(self):
        self.serial.write("R,0B")
        poll_response = self.serial.read()
        poll_responses_parsed = VMCPollResponseParser.parse(poll_response[2:])
        return poll_responses_parsed

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
