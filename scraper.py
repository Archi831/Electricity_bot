import requests, sys, json
from datetime import datetime
from bs4 import BeautifulSoup

def extract_digits(input_string):
    try:
        digits = ''.join([char for char in input_string if char.isdigit()])
        digit1 = str(digits)[0:2]
        digit2 = str(digits)[4:6]
        dur = str(digits)[8]
        digits = [digit1, digit2, dur]
        return digits
    except:
        return None
    
def parse_scales(scales):
    parsed_data = []
    for i in scales:
        if sys.getsizeof(i) == 48:
            for l in i:
                digits = extract_digits(str(l))
                if digits:
                    parsed_data.append(digits)
    return parsed_data
                

def scrape_data():
    cher = {"Today" : {}, "Tomorrow" : {}}
    for cherga in range(1,7):
        Url = f"https://zakarpat.energy-ua.info/cherga/{cherga}"
        r = requests.get(Url)
        soup = BeautifulSoup(r.content, "html.parser")
        scales = soup.find_all("div", class_="grafik_string")

        if len(scales)>1:
            cher["Today"][f'{cherga}'] = parse_scales(scales[0])
            cher["Tomorrow"][f'{cherga}'] = parse_scales(scales[1])
    
    return cher

if __name__ == "__main__":
    cher_data = scrape_data()
    timestamp = datetime.now().strftime("%D %H:%M:%S")
    print("Refreshed", timestamp)    
    
    with open('time.json', 'w') as file:
        json.dump(cher_data, file, indent=4)