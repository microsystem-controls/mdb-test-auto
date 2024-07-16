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