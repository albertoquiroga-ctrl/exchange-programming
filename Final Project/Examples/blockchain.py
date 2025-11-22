from web3 import Web3
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup


def extract_tag(address):
    url = f'https://etherscan.io/address/{address}'

    # Send a GET request to the URL
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find(id="ContentPlaceHolder1_divLabels").text.strip().split(" ")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")


def get_highvalue_transaction(block, threshold):
    latest_block = web3.eth.get_block(block)

    print(f"Block Number: {latest_block.number}")
    print(f"Number of Transactions in Block: {len(latest_block.transactions)}")

    # Step 3: Filter High-Value Transactions
    high_value_threshold = web3.to_wei(threshold, 'ether')  # Transactions > 100 ETH
    high_value_transactions = []

    for tx_hash in latest_block.transactions:
        tx = web3.eth.get_transaction(tx_hash)

        if tx.value > high_value_threshold:
            high_value_transactions.append({
                "hash": tx.hash.hex(),
                "from": tx['from'],
                "to": tx['to'],
                "value": web3.from_wei(tx.value, 'ether'),
                "from_tag": extract_tag(tx['from']),
                "to_tag": extract_tag(tx['to'])
            })

    # Display high-value transactions
    print("\nHigh-Value Transactions (> 10 ETH):")
    for tx in high_value_transactions:
        print(tx)

    return high_value_transactions


infura_url = "https://mainnet.infura.io/v3/32115b6750454322bf382e4fa3e9f467"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check connection
if web3.is_connected():
    print("Connected to Ethereum blockchain")
else:
    print("Failed to connect")
    exit()

get_highvalue_transaction(21229102, 1)