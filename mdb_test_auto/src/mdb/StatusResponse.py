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