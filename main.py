import requests
import argparse
import sys
from PIL import Image
import io


def getting_r(server_address, parms):
    res = requests.get(server_address, parms)
    if not res:
        print(parms)
        print("HTTP status:", res.status_code, "(", res.reason, ")")
        sys.exit(1)
    return res


parser = argparse.ArgumentParser()
parser.add_argument("address", type=str)
parser.add_argument("address1", type=str)
args = parser.parse_args()

server = "http://geocode-maps.yandex.ru/1.x/"
apik = "40d1649f-0493-4b70-98ba-98533de7710b"
parms = {
    "apikey": apik,
    "geocode": [args.address + args.address1],
    "format": "json"}

response = getting_r(server, parms)
json_resp = response.json()
cors = json_resp["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
fl_cors = tuple(map(float, cors.split()))
cors = cors.replace(" ", ",")

server = "https://search-maps.yandex.ru/v1/"
apik = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
search_text = "аптека"
parms = {
    "apikey": apik,
    "text": search_text,
    "lang": "ru_RU",
    "ll": cors,
    "results": 10,
    "format": "json"}
response = getting_r(server, parms)
json_resp = response.json()
orgs = json_resp["features"]

pointers = []
for elem in orgs:
    coors_d = elem["geometry"]["coordinates"]
    try:
        wt = elem["properties"]["CompanyMetaData"]["Hours"]["Availabilities"][0]
    except KeyError:
        pointers.append(",".join(map(str, coors_d)) + ",pm2grm")
    else:
        if "TwentyFourHours" in wt:
            pointers.append(",".join(map(str, coors_d)) + ",pm2gnm")
        else:
            pointers.append(",".join(map(str, coors_d)) + ",pm2blm")

server = "http://static-maps.yandex.ru/1.x/"
parms = {
    "l": "map",
    "pt": "~".join(pointers)
}
response = getting_r(server, parms)
Image.open(io.BytesIO(response.content)).show()
