class CoinsDispensedResponse:
    def __init__(self, num_coins_dispensed, coin_type, coins_in_tube):
        self.num_coins_dispensed = num_coins_dispensed
        self.coin_type = coin_type
        self.coins_in_tube = coins_in_tube

    def __str__(self):
        return (f"Coins Dispensed Manually - Number: {self.num_coins_dispensed}, "
                f"Coin Type: {self.coin_type}, Coins in Tube: {self.coins_in_tube}")