from dataclasses import dataclass
from typing import List


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