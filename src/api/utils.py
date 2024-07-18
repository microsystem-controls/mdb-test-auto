from mdb.MDBSetupResponse import MDBSetupResponse
from api.schema import DeviceInfo


def create_device_info(device_info_data: str,device_setup_data: MDBSetupResponse) -> DeviceInfo:
    return DeviceInfo(serial_number = device_info_data[9 : 33: 2], coin_scaling_factor = device_setup_data.coin_scaling_factor,
                      coin_type_routing = device_setup_data.coin_type_routing,coin_type_credit = device_setup_data.coin_type_credit,
                      decimal_places=device_setup_data.decimal_places)
