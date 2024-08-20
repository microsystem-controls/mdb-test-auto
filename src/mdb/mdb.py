from logging import Logger
import time

from mdb.CoinsDepositedResponse import CoinsDepositedResponse
from mdb.SlugResponse import SlugResponse

from .MDBSetupResponse import MDBSetupResponse
from .VMCPollResponseParser import VMCPollResponseParser
from .serialcomm import SerialComm
from .CoinTypesToDespense import CoinTypesToDespense
import csv
from io import StringIO


class MDB:
    def __init__(self):
        self.serial = SerialComm(Logger("mdb"))
        self.test_status = "stopped"
        self._cancel_test_flag = False
        self.device_info: MDBSetupResponse = None
        self._initialise_changer()
        self.test_result: AcceptanceTestResult = None
        
       

    def _initialise_changer(self):
        self.serial.write("M,1")
        if self.serial.read() != "m,ACK":
            raise Exception("Failed to set master mode")
       # enabling coins
        self.serial.write("R,0C,FFFFFFFF")
        self.serial.read()
        self.device_info = self.id()[1]

    def dispense(self, value: int, number:int):
        coin_index_to_dispense = self.device_info.coin_type_credit.index(value // self.device_info.coin_scaling_factor)
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

    def dispense_and_wait_to_return(self, coin_type: int, dispense: bool, timeout_in_seconds:int):
        if dispense:
            self.dispense(coin_type, 1)
            print(f"coin {coin_type} dispensed")
        start_time = time.time()
        while True:
            if self._cancel_test_flag:
                return
            if time.time() - start_time > timeout_in_seconds:
                return "lost"
            poll_results = self.poll()
            if len(poll_results) > 0:
                poll_result = poll_results[0] 
                if isinstance(poll_result, CoinsDepositedResponse):
                    if poll_result.coin_type == coin_type:
                        return "accepted"
                    else:
                        return "cross"
                elif isinstance(poll_result, SlugResponse):
                    return "rejected"
                

    def run_test(self, coin_types:list[CoinTypesToDespense]):
        self.test_result = AcceptanceTestResult(coin_types)
        self.test_status = "running"
        poll_result = self.poll()
        for coin_type in coin_types:
            dispense_a_coin = True
            while coin_type.dispenses > 0:
                if self._cancel_test_flag:
                    break
                response = self.dispense_and_wait_to_return(coin_type.type, dispense_a_coin, 10)
                print(response)
                if response == "rejected":
                    self.test_result.coin_results[coin_type.type].rejected += 1
                    dispense_a_coin = False
                elif response == "lost":
                    self.test_result.coin_results[coin_type.type].lost += 1
                    dispense_a_coin = True
                    coin_type.dispenses -= 1
                else:
                    dispense_a_coin = True
                    self.test_result.coin_results[coin_type.type].accepted += 1
                    coin_type.dispenses -= 1
                time.sleep(1)
        self._cancel_test_flag = False
        self.test_status = "stopped"

    def cancel_running_test(self):
        self._cancel_test_flag = True
        
class CoinCycleAcceptanceResult:
    def __init__(self, cycle_details: CoinTypesToDespense):
        self.coin_type = cycle_details.type
        self.number_of_dispenses = cycle_details.dispenses
        self.accepted = 0
        self.rejected = 0
        self.lost = 0
        self.total = cycle_details.dispenses

class AcceptanceTestResult:
    def __init__(self, coin_types: list[CoinTypesToDespense]):
        self.coin_results:dict[int, CoinCycleAcceptanceResult] = {}
        for coin_type in coin_types:
            self.coin_results[coin_type.type] = CoinCycleAcceptanceResult(coin_type)     

    def to_csv(self):
        header = "coin type,number of dispenses,accepted,rejected,lost,total"
        rows = []
        rows.append(header)
        for cycle_result in self.coin_results.values():
            row_data = [cycle_result.coin_type, cycle_result.number_of_dispenses, cycle_result.accepted, cycle_result.rejected, cycle_result.lost, cycle_result.total]
            row_str= map(str, row_data)
            rows.append(",".join(row_str))

        
        return "\n".join(rows)

    


    

