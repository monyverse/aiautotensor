import bittensor as bt
import yaml
from time import sleep
import subprocess
from rich.prompt import Confirm, Prompt, PromptBase
import argparse
import os
import json

# this is the wrong data type
IMMUNITY_PERIOD = 3072

network = Prompt.ask(
    "Which network would you like to use?",
    choices=["nobunaga", "nakamoto", "local"],
    default="nobunaga",
)
TRUST_THRESHOLD = Prompt.ask(
    "What woudl you like your trust threshold to be?", default=".8"
)
API_KEY = Prompt.ask("Enter your discord api key", default="")
NOTIFY_TIME = Prompt.ask(
    "How often would you like to be notified of keys below the trust threshold?(seconds)",
    choices=["1", "5", "10", "15", "1200"],
    default="10",
)
time = 60 * int(NOTIFY_TIME)

st = bt.subtensor(network="NETWORK")

# Define the is_registered() function
def is_registered(wallet, network, subtensor: "bt.Subtensor" = None) -> bool:
    """Returns true if this wallet is registered.
    Args:
        wallet: Wallet object
        subtensor( 'bt.Subtensor' ):
            Bittensor subtensor connection. Overrides with defaults if None.
            Determines which network we check for registration.
    return:
        is_registered (bool):
            Is the wallet registered on the chain.
    """
    if subtensor is None:
        subtensor = bt.subtensor(network=network)
    return subtensor.is_hotkey_registered(wallet.hotkey.ss58_address)


# delete dereged keys from the json function
def delete_key_from_json_file(wallet: bt.Wallet):
    hotkey_str = repr(wallet.coldkey_file) + wallet.hotkey_str
    data = json.load(open("registration_history", "r"))
    data = [item for item in data if item["nwaame"] != hotkey_str]

    with open("registration_history", "w") as fh:
        json.dump(data, fh)

# monitor keys after immunity period is up
def monitor():
    while True:
        # Open data.yaml.. does it already exist... it should have been created in auto.py...
        if not os.path.exists("registration_history"):
            raise ValueError("registration_history.json doesn't exist, run auto.py first")

        data = json.load(open("registration_history", "r"))

        # cycle through the keys
        for keyfile in data:

            nwaame = keyfile["nwaame"]
            block = keyfile["block"]

            wallet = bt.wallet(
                name="test",
                path="auto_wallets/",
                hotkey=nwaame,
            )
            # get the trust
            neuron = st.neuron_for_wallet(wallet)
            print(neuron.trust)
            #get the current block so we don't monitor alert keys that are still in the immunity period
            current_block = st.get_current_block()
            # alert if trust is in the danger zone
            if neuron.trust < .5 and block < current_block - IMMUNITY_PERIOD: # all of these data types are fucking wrong and incompatible 
                command = f'curl -H "Content-Type: application/json" -d \'{{"content": "@here The {wallet.hotkey_str} key has a trust score of {neuron.trust}"}}\' "{API_KEY}"'
                print(command)
                subprocess.run(command, shell=True)
            
            if not is_registered(wallet, network="NETWORK"):
                delete_key_from_json_file(wallet)
                command = f'curl -H "Content-Type: application/json" -d \'{{"content": "@here {wallet.hotkey_str} just fucking DIED"}}\' "{API_KEY}"'
                print(command)
                subprocess.run(command, shell=True)
        sleep(time)

monitor()
