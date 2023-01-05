import bittensor as bt
import yaml
import time
import subprocess
from rich.prompt import Confirm, Prompt, PromptBase
import argparse
import os

NETWORK = Prompt.ask("Which network would you like to use?", choices=["nobunaga", "nakamoto", "local"], default="nobunaga")
TRUST_THRESHOLD = Prompt.ask("What woudl you like your trust threshold to be?", default=".5")
API_KEY = Prompt.ask("Enter your discord api key", default="")
NOTIFY_TIME = Prompt.ask("How often would you like to be notified of keys below the trust threshold?(minutes)", choices=["1", "5", "10", "15", "20"], default="10")
if NOTIFY_TIME == "1":
    time = 60
if NOTIFY_TIME == "5":
    time = 300
if NOTIFY_TIME == "10":
    time = 600
if NOTIFY_TIME == "15":
    time = 900
if NOTIFY_TIME == "20":
    time = 1200

def main():
    while True:
        with open('config.yaml', 'r') as file:
            machs = yaml.safe_load(file)
        for machine_id in machs.keys():
            machine_config = machs[machine_id]
            for gpu_index, gpu_config in enumerate(machine_config):
                wallet = bt.wallet(name=(gpu_config['wallet']), path="auto_wallets/",
                                   hotkey=str(gpu_config['keyfile']))
                st = bt.subtensor(network="NETWORK")
                neuron = st.neuron_for_wallet(wallet)
                print(neuron.trust)
                if neuron.trust < TRUST_THRESHOLD:
                    command = f"curl -H \"Content-Type: application/json\" -d '{{\"content\": \"@here The {wallet.hotkey_str} key on {machine_id} has a trust score of {neuron.trust}\"}}' \"{API_KEY}\""
                    print(command)
                    subprocess.run(command, shell=True)
        time.sleep(time)
main()
