import requests
import random
import time
import urllib.parse
import json

def load_user_data(filename):
    with open(filename, "r") as file:
        data = file.readlines()
    
    user_data = []
    for line in data:
        parsed_data = urllib.parse.parse_qs(line.strip())
        user_info = parsed_data.get('user', [None])[0]
        if user_info:
            user_info_decoded = urllib.parse.unquote(user_info)
            user_info_dict = json.loads(user_info_decoded)
            user_id = user_info_dict.get("id")
            username = user_info_dict.get("username")
            user_data.append((user_id, username, line.strip()))
    
    return user_data

# URLs and Headers
login_url = "https://ago-api.hexacore.io/api/app-auth"
user_exists_url = "https://ago-api.hexacore.io/api/user-exists"
balance_url_template = "https://ago-api.hexacore.io/api/balance/{}"
cekin_url = "https://ago-api.hexacore.io/api/daily-checkin"
cek_taps_url = "https://ago-api.hexacore.io/api/available-taps"
buy_taps_url = "https://ago-api.hexacore.io/api/buy-tap-passes"
klik_url = "https://ago-api.hexacore.io/api/mining-complete"

headers = {
    "Content-Type": "application/json",
    "Origin": "https://ago-wallet.hexacore.io",
    "Referer": "https://ago-wallet.hexacore.io/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}

def login_from_data(data_line):
    payload = {"data": data_line}
    print("Mengambil Data Untuk Login")
    response = requests.post(login_url, json=payload, headers=headers)
    try:
        response_data = response.json()
        token = response_data.get("token")
        if token:
            parsed_data = urllib.parse.parse_qs(data_line)
            user_info = parsed_data.get('user', [None])[0]
            if user_info:
                user_info_decoded = urllib.parse.unquote(user_info)
                user_info_dict = json.loads(user_info_decoded)
                user_id = user_info_dict.get("id")
                print("Token berhasil didapatkan")
                return token, user_id
    except requests.exceptions.JSONDecodeError:
        print("Gagal mendekode respons JSON. Konten respons:")
        print(response.text)
    return None, None

def check_user_exists(token):
    headers['Authorization'] = token
    response = requests.get(user_exists_url, headers=headers)
    return response.json().get("exists")

def get_balance(user_id, token):
    balance_url = balance_url_template.format(user_id)
    headers['Authorization'] = token
    response = requests.get(balance_url, headers=headers)
    
    if response.status_code == 200:
        try:
            balance_data = response.json()
            return balance_data.get("user_id"), balance_data.get("balance")
        except requests.exceptions.JSONDecodeError:
            print("Failed to decode JSON response during balance retrieval. Response content:")
            print(response.text)
            return None, None
    else:
        print(f"Failed to retrieve balance. HTTP Status Code: {response.status_code}")
        print("Response content:")
        print(response.text)
        return None, None

def daily_checkin(token, day):
    headers['Authorization'] = token
    cekin_payload = {"day": day}
    response = requests.post(cekin_url, json=cekin_payload, headers=headers)
    try:
        response_data = response.json()
        available_at = response_data.get("available_at")
        success = response_data.get("success")
        print(f"Check for day {day} | Status Daily Check-in Day {day}: Success={success}, Available at={available_at}")
        return available_at, success
    except json.JSONDecodeError:
        print(f"Check for day {day} | Status Daily Check-in Day {day}: Failed or Invalid Response")
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"Check for day {day} | Status Daily Check-in Day {day}: Failed or Invalid Response")
        return None, None

def check_available_taps(token):
    headers['Authorization'] = token
    response = requests.get(cek_taps_url, headers=headers)
    return response.json().get("available_taps")

def buy_taps(token):
    headers['Authorization'] = token
    buy_taps_options = ["1_days", "3_days", "7_days"]
    buy_taps_payload = {"name": random.choice(buy_taps_options)}
    
    response = requests.post(buy_taps_url, json=buy_taps_payload, headers=headers)
    
    try:
        response_data = response.json()
        return response_data.get("success")
    except requests.exceptions.JSONDecodeError:
        print("Gagal mendekode respons JSON. Konten respons:")
        print(response.text)
        return None

def mining_complete(token):
    headers['Authorization'] = token
    klik_payload = {"taps": random.randint(50, 150)}
    response = requests.post(klik_url, json=klik_payload, headers=headers)
    print(f"Klik Payload: {klik_payload}")
    return response.json().get("success")

def main():
    data_file = "data.txt"
    user_data_list = load_user_data(data_file)
    
    while True:
        for user_id, username, data_line in user_data_list:
            print(f"\nProcessing user: {username} (ID: {user_id})")
            token, user_id = login_from_data(data_line)
            if token:
                print("Token: Sukses Mendapatkan Token")

                exists = check_user_exists(token)
                print(f"User Exists: {exists}")

                user_id, balance = get_balance(user_id, token)
                print(f"User ID: {user_id}, Balance: {balance}")
                
                # Loop through each day from 1 to 20 for daily check-in
                for day in random.sample(range(1, 21), 20):
                    available_at, success = daily_checkin(token, day)
                    if available_at is not None and success is not None:
                        print(f"Status Daily Check-in Day {day}: Success={success}, Available at={available_at}")
                    else:
                        print(f"Status Daily Check-in Day {day}: Failed or Invalid Response")
                    time.sleep(0)  # Delay between check-ins for realism


                available_taps = check_available_taps(token)
                print(f"Available Taps: {available_taps}")

                success = buy_taps(token)
                print(f"Buy Taps: Success={success}")

                success = mining_complete(token)
                print(f"Mining Complete: Success={success}")

                delay = random.randint(3, 5)
                print(f"Waiting for {delay} seconds before processing next user...")
                for i in range(delay, 0, -1):
                    print(f"{i} seconds remaining...", end="\r")
                    time.sleep(1)
            else:
                print("Login failed!")

        print("\nAll users processed. Starting the next cycle...")
        time.sleep(15)

if __name__ == "__main__":
    main()
