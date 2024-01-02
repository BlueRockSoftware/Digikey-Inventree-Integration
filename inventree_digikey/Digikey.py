from digikey import product_details, status_salesorder_id, salesorder_history
import os
import configparser
from pathlib import Path
from datetime import datetime
from dateutil import parser

from .ImageManager import ImageManager

config = configparser.ConfigParser()
config_path = Path(__file__).resolve().parent / 'config.ini'
config.read(config_path)

os.environ['DIGIKEY_CLIENT_ID'] = config['DIGIKEY_API']['CLIENT_ID']
os.environ['DIGIKEY_CLIENT_SECRET'] = config['DIGIKEY_API']['CLIENT_SECRET']
os.environ['DIGIKEY_CLIENT_SANDBOX'] = 'False'
os.environ['DIGIKEY_STORAGE_PATH'] = '.'

def get_part_from_part_number(partnum: str, prompt=True):
    raw = product_details(partnum)
    print(raw)
    part = DigiPart(raw)
    part.injest_api(prompt)
    return part


def get_order_from_order_number(order_number: str):
    all_orders = salesorder_history(start_date="2021-01-01", end_date=datetime.now().strftime("%Y-%m-%d"))
    found_order = None
    #print(all_orders)
    for order in all_orders:
        #print(f"Order: {order.salesorder_id}")
        if str(order.salesorder_id) == order_number:
            found_order = order
            break

    raw = status_salesorder_id(order_number)
    print(raw)
    order = DigiOrder(raw)
    if found_order is not None:
        order.order_date = parser.parse(found_order.date_entered)
    else:
        order.order_date = datetime.now()
    #print(f"Order Date: {order.order_date}, Found Order: {found_order}")
    return order


def get_order_history(start_date: str, end_date: str):
    all_orders = salesorder_history(start_date=start_date, end_date=end_date)
    print(all_orders)
    for order in all_orders:
        order_date = parser.parse(order.date_entered).strftime("%Y-%m-%d")
        print(f"Order: {order.salesorder_id}, Date: {order_date}")


class DigiPart:
    def __init__(self, api_value):
        self.name = None
        self.supplier = "Digikey"
        self.digi_part_num = None
        self.mfg_part_num = None
        self.manufacturer = None
        self.description = None
        self.link = None
        self.price_breaks = []
        self.raw_value = api_value
        self.parameters = []
        self.picture = None
        self.thumbnail = None
        self.htsus = None
        self.catagory = None


    def injest_api(self, prompt=True):
        self.manufacturer = self.raw_value.manufacturer.value
        self.mfg_part_num = self.raw_value.manufacturer_part_number
        self.description = self.raw_value.product_description
        self.link = self.raw_value.product_url
        self.digi_part_num = self.raw_value.digi_key_part_number
        self.picture = self.raw_value.primary_photo
        self.htsus = self.raw_value.htsus_code
        self.category = self.raw_value.limited_taxonomy.value
        for raw_param in self.raw_value.parameters:
            cleaned_param = (raw_param.parameter, raw_param.value)
            self.parameters.append(cleaned_param)
        
        if prompt:
            self.prompt_part_name()
        else:
            self.set_part_name(self.raw_value.manufacturer_part_number)


    def set_part_name(self, name: str):
        self.name = name


    def prompt_part_name(self):
        found_name = self.raw_value.manufacturer_part_number
        print(f"Found {found_name} - Would you like to use this name (y/n)")
        ans = input("> ")
        if ans == "y":
            self.set_part_name(found_name)
        else:
            print("Type a new name")
            name = input("> ")
            self.set_part_name(name)


    def _extract_picture(self):
        for media in self.raw_value.media_links:
            print(media.media_type)
            if "Product Photos" in media.media_type:
                self.picture = "%s" % media.url


class DigiLineItem:
    def __init__(self, api_value) -> None:
        self.raw_value = api_value
        self.injest_api()

    def injest_api(self):
        self.digi_key_part_number = self.raw_value.digi_key_part_number
        self.manufacturer = self.raw_value.manufacturer
        self.manufacturer_part_number = self.raw_value.manufacturer_part_number
        self.product_description = self.raw_value.product_description
        self.quantity = self.raw_value.quantity
        self.unit_price = self.raw_value.unit_price
        self.total_price = self.raw_value.total_price
        self.invoice_id = self.raw_value.invoice_id

class DigiOrder:
    def __init__(self, api_value):
        self.raw_value = api_value
        self.order_number = None
        self.line_items = []
        self.order_date = None
        self.injest_api()

    def injest_api(self):
        self.order_number = self.raw_value.salesorder_id
        for line_item in self.raw_value.line_items:
            self.line_items.append(DigiLineItem(line_item))
