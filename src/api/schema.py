from pydantic import BaseModel


class DeviceInfo(BaseModel):
    serial_number: str
    coin_type_credit: list[int]
    coin_type_routing: list[int]
    coin_scaling_factor: int
    decimal_places: int


