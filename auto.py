import argparse
import os
import subprocess
from time import sleep
import bittensor as bt
import torch
import yaml


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


def check_is_running(proc_name: str) -> bool:

    pm2_output = subprocess.check_output(["pm2",  "id", proc_name])
    return len(pm2_output) > 3


def kill_pm2(proc_name: str):

    os.system(f"pm2 delete {proc_name}")


def make_proc_name(gpu_config, wallet) -> str:
    return f"{gpu_config['name']}_{wallet.hotkey_str}"


# Define the deploy_core_server function
def deploy_core_server(
    gpu_index,
    gpu_config,
    wallet: "bt.Wallet"
):

    pm2_process_name = make_proc_name(gpu_config, wallet)
    is_running = check_is_running(pm2_process_name)
    if is_running is False:
        command = (
            f"pm2 start "
            f"~/.bittensor/bittensor/bittensor/_neuron/text/core_server/main.py "
            f"--name {pm2_process_name} --time --interpreter python3 -- "
            f"--logging.debug "
            f"--subtensor.network {gpu_config['network']} "
            f"--neuron.device cuda:{gpu_index} "
            f"--neuron.model_name {gpu_config['model']} "
            f"--axon.port {gpu_config['port']} "
            f"--wallet.name {gpu_config['wallet']} "
            f"--wallet.hotkey {wallet.hotkey_str}"
        )
        # Run the command in the command line
        subprocess.run(command, shell=True)

        # Set the done flag to True
        is_running = True
        pass


num_gpus = torch.cuda.device_count()

with open('config.yaml', 'r') as file:
    machs = yaml.safe_load(file)

if os.getenv("MACHINE_ID") is None:
    raise ValueError(("You must specify the environment variable MACHINE_ID prior to running this script"))
assert os.getenv("MACHINE_ID") in machs.keys()


while True:
    for machine_id in machs.keys():
        machine_config = machs[machine_id]
        for gpu_index, gpu_config in enumerate(machine_config):
            # Create a new wallet object for each GPU
            wallet = bt.wallet(name=(gpu_config['wallet']), path="auto_wallets/",
                               hotkey=str(gpu_config['keyfile']))
            # Check if the wallet is registered
            if not is_registered(wallet, network=gpu_config["network"]):
                expected_proc_name = make_proc_name(gpu_config=gpu_config, wallet=wallet)
                if check_is_running(expected_proc_name):
                    kill_pm2(expected_proc_name)
                    command += "curl -H \"Content-Type: application/json\" -d '{\"content\": \"@here you lost a hotkey! :(\"}' \"""
                    print(command)
                    subprocess.run(command, shell=True)
                sleep(10)

            while not is_registered(wallet, network=gpu_config['network']):

                range_string = " ".join(str(i) for i in range(num_gpus))  # not sorry ala
                # Register the wallet using all GPUs.
                command = (
                    f"btcli register "
                    f"--subtensor.network {gpu_config['network']} "
                    f"--wallet.name {wallet.name} "
                    f"--wallet.hotkey {wallet.hotkey_str} "
                    f"--wallet.path auto_wallets/ "
                    f"--cuda --cuda.dev_id {range_string} "
                    f"--cuda.TPB 512 "
                    f"--cuda update_interval 250_000 "
                    f"--no_prompt "
                )
                # command += "&& curl -H \"Content-Type: application/json\" -d '{\"content\": \"@here a new key is Registered! :)\"}' \"""
                print(command)
                subprocess.run(command, shell=True)

            if machine_id == os.getenv("MACHINE_ID"):
                deploy_core_server(gpu_index, gpu_config, wallet)
                
            sleep(10)
