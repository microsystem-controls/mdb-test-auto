from mdb.CoinsDepositedResponse import CoinsDepositedResponse
from mdb.CoinsDispensedResponse import CoinsDispensedResponse
from mdb.StatusResponse import StatusResponse
from mdb.SlugResponse import SlugResponse


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