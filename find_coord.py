import requests
def find_coord(address):
    r_url = "https://dapi.kakao.com/v2/local/search/address.json"
    header = {
        "Authorization": "KakaoAK 2353df1ebd0f9ff60a6100477bf3ec26"
    }
    query = {
        "query": address
    }
    api_result = requests.get(r_url, headers=header, params=query).json()["documents"][0]["address"]
    coord = (float(api_result["x"]), float(api_result["y"]))

    return coord
