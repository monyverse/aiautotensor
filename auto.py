import argparse
import subprocess
from time import sleep
from typing import Optional
import math
from typing import List, Optional, Sequence
from collections import defaultdict
import torch
from bittensor import dataset as btdataset
from datasets import load_dataset
from tqdm import tqdm
import torch.nn.functional as F
from torch.nn import CrossEntropyLoss
from sklearn import metrics

import bittensor as bt
import torch

import yaml

with open('config.yaml', 'r') as file:
    machs = yaml.safe_load(file)
    machine_config1 = machs['machine1']
    machine_config2 = machs['machine2']

    #print(machs['machine1']['gpu0']['name'])

#NETWORK = "nobunaga"


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


# Define the deploy_core_server function
def deploy_core_server(
    gpu_index,
    gpu_config,
    wallet: "bt.Wallet"
):
    is_running = False
    if is_running is False:
        command = (
            f"--name autominer_{wallet.hotkey_str} --time --interpreter python3 -- "
            f"--logging.debug "
            f"--subtensor.network {gpu_config['network']} "
            f"--neuron.device cuda:{gpu_index} "
            f"--wallet.name test "
            f"--wallet.hotkey {wallet.hotkey_str}"
        )
        # Run the command in the command line
        subprocess.run(command, shell=True)

        # Set the done flag to True
        is_running = True
        pass

parser = argparse.ArgumentParser(
    prog="Autominer", description="drains your wallet and immediately burns all your Tao"
)
parser.add_argument(
    "--num_gpus",
    default=0,
    type=int,
    help="How many GPUs to use for registration. Defaults to all available GPUs.",
)

args = parser.parse_args()

# Get the number of GPUs on the system
if args.num_gpus == 0:
    num_gpus = torch.cuda.device_count()
else:
    num_gpus = args.num_gpus



for gpu_index, gpu_config in enumerate(machine_config1):
    # Create a new wallet object for each GPU
    wallet = bt.wallet(name=(gpu_config['wallet']), hotkey=str(gpu_config['keyfile']))
    #wallet = bt.wallet(name="test", hotkey=str(i))
    wallet.create()

    # Check if the wallet is registered
    while not is_registered(wallet, network=gpu_config['network']):

        range_string = " ".join(str(i) for i in range(num_gpus))  # not sorry ala
        # Register the wallet using all GPUs.
        command = (
            f"btcli register "
            f"--subtensor.network {gpu_config['network']} "
            f"--wallet.name {wallet.name} "
            f"--wallet.hotkey {wallet.hotkey_str} "
            f"--cuda --cuda.dev_id {range_string} "
            f"--cuda.TPB 512 "
            f"--cuda update_interval 250_000 "
            f"--no_prompt "
        )
        command += "&& curl -H \"Content-Type: application/json\" -d '{\"content\": \"@here a new key is Registered!\"}' \"https://canary.discord.com/api/webhooks/1040675301476278383/fxw42Qu0zduw-Ivk7_avfPK4_RuVoygO3nOQauEZHjZbHPZUtrf_AFQTOIMJxW9JVjqf\""
        print(command)
        subprocess.run(command, shell=True)

    else:


    deploy_core_server(gpu_index, gpu_config, wallet)
    sleep(10)
