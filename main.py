import argparse
import requests
import json
import pandas as pd
from web3 import Web3
from decimal import Decimal, ROUND_HALF_UP

# Setup web3 connection
w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
print("Web3 Connected:", w3.is_connected())


def fetch_abi(address, api_key):
    """Fetches the ABI for a contract from BscScan."""
    url = f"https://api.bscscan.com/api?module=contract&action=getabi&address={address}&apikey={api_key}"
    response = requests.get(url)
    response.raise_for_status()  # Raises an exception if the request failed
    return json.loads(response.content)['result']


# Load API key from config.json
with open('api_key.json', 'r') as config_file:
    config = json.load(config_file)
    api_key = config.get('bscscan_api_key')

# Contract setup
contract_address = '0x18b2a687610328590bc8f2e5fedde3b582a49cda'  # PancakeSwap contract address
checksum_address = w3.to_checksum_address(contract_address)

# Fetch ABI and set up contract
abi = fetch_abi(contract_address, api_key)
contract = w3.eth.contract(address=checksum_address, abi=abi)


def get_epoch_result(epoch):
    """Get the result for a specific epoch."""
    try:
        round_data = contract.functions.rounds(epoch).call()
        if round_data[5] > round_data[4]:  # Assuming closePrice is at index 5 and lockPrice at index 4
            return "Bull"
        elif round_data[5] < round_data[4]:
            return "Bear"
        elif round_data[5] == round_data[4]:
            return "Draw"
        else:
            return "Error"
    except Exception as e:
        print(f"Error fetching epoch {epoch}: {e}")
        return "Error"


def get_winning_odds(epoch, position):
    """Fetches winning odds for a specific epoch and position."""
    try:
        round_data = contract.functions.rounds(epoch).call()
        bull_amount_wei = round_data[9]
        bear_amount_wei = round_data[10]
        total_amount_wei = bull_amount_wei + bear_amount_wei

        # Convert from Wei to BNB
        bull_amount = Web3.from_wei(bull_amount_wei, 'ether')
        bear_amount = Web3.from_wei(bear_amount_wei, 'ether')
        total_amount = Web3.from_wei(total_amount_wei, 'ether')

        if total_amount == 0:
            return 0

        if position == "Bear":
            odds = total_amount / bear_amount if bear_amount > 0 else 0
        elif position == "Bull":
            odds = total_amount / bull_amount if bull_amount > 0 else 0
        else:
            odds = 0

        # Round to the nearest hundredth
        return Decimal(odds).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except Exception as e:
        print(f"Error fetching winning odds for epoch {epoch}: {e}")
        return 0


def process_epoch(epoch_number):
    """Process an epoch to get its result and winning odds."""
    result = get_epoch_result(epoch_number)
    bull_odds = get_winning_odds(epoch_number, "Bull")
    bear_odds = get_winning_odds(epoch_number, "Bear")
    return [epoch_number, result, bull_odds, bear_odds]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch PancakeSwap round results")
    parser.add_argument("--latest_n", type=int, help="Get results for the latest N epochs")
    parser.add_argument("--start_epoch", type=int, help="Start epoch number")
    parser.add_argument("--end_epoch", type=int, help="End epoch number")
    args = parser.parse_args()

    # Determine the range of epochs to process
    if args.latest_n:
        latest_epoch = contract.functions.currentEpoch().call()
        start_epoch = max(1, latest_epoch - args.latest_n - 1)  # Adjust to exclude the latest 2 epochs
        end_epoch = latest_epoch - 2  # Exclude the latest 2 epochs
    elif args.start_epoch and args.end_epoch:
        start_epoch = args.start_epoch
        end_epoch = args.end_epoch
    else:
        # If no arguments are provided, prompt the user
        while True:
            user_choice = input(
                "Would you like to fetch the latest N epochs (enter 'latest') or a range (enter 'range')? ")
            if user_choice.lower() == 'latest':
                latest_n = int(input("Enter the number of latest epochs to fetch: "))
                latest_epoch = contract.functions.currentEpoch().call()
                start_epoch = max(1, latest_epoch - latest_n - 1)  # Adjust to exclude the latest 2 epochs
                end_epoch = latest_epoch - 2  # Exclude the latest 2 epochs
                break
            elif user_choice.lower() == 'range':
                start_epoch = int(input("Enter the start epoch: "))
                end_epoch = int(input("Enter the end epoch: "))
                break
            else:
                print("Invalid input. Please enter 'latest' or 'range'.")

    # Fetch data for each epoch and store in a list
    results = []
    for epoch_number in range(start_epoch, end_epoch + 1):
        try:
            epoch_data = process_epoch(epoch_number)
            print(f"Processed Epoch {epoch_number}: {epoch_data}")
            results.append(epoch_data)
        except Exception as e:
            print(f"Error processing epoch {epoch_number}: {e}")

    # Save results to CSV
    results_df = pd.DataFrame(results, columns=['Epoch', 'Result', 'Bull Odds', 'Bear Odds'])
    results_df.to_csv('epoch_results.csv', index=False)
    print("Results saved to epoch_results.csv")
