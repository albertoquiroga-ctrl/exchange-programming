import requests
import json
import time


# Complete the following function to get HSBC property valuation
# Use it to find the valuation of
# - Flat A, Block/Tower 1,Sorrento,Tsimshatsui,Kowloon of 8 - 15/F


def get_hsbc_valuation(zoneId, districtId, estateId, blockId, floor, flat):

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'DNT': '1',
        'Origin': 'https://www.hsbc.com.hk',
        'Referer': 'https://www.hsbc.com.hk/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'client_id': '5eca677638ab454086052a18da4e2cb0',
        'client_secret': 'd35073Cf96B64b1E9CE25f4E07746300',
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    json_data = {
        'locale': 'en_HK',
        'zoneId': zoneId,
        'districtId': districtId,
        'estateId': estateId,
        'blockId': blockId,
        'floor': floor,
        'flat': flat,
    }

    response = requests.post(
        'https://rbwm-api.hsbc.com.hk/digital-pws-tools-mortgages-eapi-prod-proxy/v1/mortgages/property-valuation',
        headers=headers,
        json=json_data,
    )

    result = response.json()

    try:
        return f"the valuation for the {floor} floor is ${result["valn"]} HKD"
    except KeyError:
        return f"valuation not found for {floor} floor"

    # Note: json_data will not be serialized by requests
    # exactly as it was in the original request.
    #data = '{"locale":"en_HK","zoneId":"2","districtId":"29","estateId":"2373","blockId":"nil,9496,nil","floor":"8","flat":"A"}'
    #response = requests.post(
    #    'https://rbwm-api.hsbc.com.hk/digital-pws-tools-mortgages-eapi-prod-proxy/v1/mortgages/property-valuation',
    #    headers=headers,
    #    data=data,
    #)


zoneId = '2'
districtId = '29'
estateId = '2373'
blockId = 'nil,9496,nil'
flat = 'A'

for floor in [8,9,10,11,12,13,14,15]:
    print(get_hsbc_valuation(zoneId, districtId, estateId, blockId, str(floor), flat))
    time.sleep(5)

