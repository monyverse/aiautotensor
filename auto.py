import argparse
import subprocess
from time import sleep
from typing import Optional

import bittensor as bt
import torch

NETWORK = "nobunaga"


# Define the is_registered() function
def is_registered(wallet, subtensor: "bt.Subtensor" = None) -> bool:
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
        subtensor = bt.subtensor(network=NETWORK)
    return subtensor.is_hotkey_registered(wallet.hotkey.ss58_address)


# Define the deploy_core_server function
def deploy_core_server(
    wallet: "bt.Wallet", vr_threshold: int = 1000, model_path: Optional[str] = None
):
    """Deploys a bittensor core_server on a GPU with VRAM usage below the specified threshold.
    Args:
            vr_threshold: VRAM threshold below which a bittensor core_server is deployed.
            vram_used: List of VRAM usage values, in bytes.
    """
    # Use the nvidia-smi command to get the VRAM usage of each GPU.
    output = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"]
    )

    # Parse the output to get the VRAM usage of each GPU.
    is_running = False
    for gpu_index, line in enumerate(output.split(b"\n")):
        try:
            vram_used = int(line.strip())
        # Last line of nvidia-smi is empty.
        except ValueError:
            break

        # If the VRAM usage is below the threshold and a core_server has not been deployed yet,
        # deploy a bittensor core_server.
        if vram_used < vr_threshold and is_running is False:
            print(
                f"Deploying bittensor core_server on GPU with "
                f"{vram_used} MB of VRAM (GPU index: {gpu_index})"
            )
            # Set the current GPU as the active device
            torch.cuda.set_device(gpu_index)

            command = (
                f"pm2 start "
                f"~/.bittensor/bittensor/bittensor/_neuron/text/core_validator/main.py "
                f"--name autominer_{wallet.hotkey_str} --time --interpreter python3 -- "
                f"--logging.debug "
                f"--subtensor.network {NETWORK} "
                f"--neuron.device cuda:{gpu_index} "
                f"--wallet.name test "
                f"--wallet.hotkey {wallet.hotkey_str}"
            )
            # Run the command in the command line
            subprocess.run(command, shell=True)

            # Set the done flag to True
            is_running = True

            # config = None
            # dataset = bt.dataset()
            # subtensor = bt.subtensor(network = "nakamoto")
            # wallet = bt.wallet(name="Nicomachus", hotkey="Eugene")
            # axon = bt.axon(port = 8000, wallet = wallet)
            # metagraph = bt.metagraph()
            # template = bt.neurons.core_server.neuron(config = config, subtensor = subtensor, wallet = wallet, axon = axon, metagraph = metagraph).run()
            # template = bt.neurons.core_validator.neuron(config = config, subtensor = subtensor, wallet = wallet, axon = axon, metagraph = metagraph).run()
            
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

for i in range(num_gpus):
    # Create a new wallet object for each GPU
    wallet = bt.wallet(name="test", hotkey=str(i))
    wallet.create()

    # Check if the wallet is registered
    while not is_registered(wallet):

        range_string = " ".join(str(i) for i in range(num_gpus))  # not sorry ala
        # Register the wallet using all GPUs.
        command = (
            f"btcli register "
            f"--subtensor.network {NETWORK} "
            f"--wallet.name {wallet.name} "
            f"--wallet.hotkey {wallet.hotkey_str} "
            f"--cuda --cuda.dev_id {range_string} "
            f"--cuda.TPB 512 "
            f"--cuda.update_interval 250_000 "
            f"--no_prompt"
        )
        print(command)
        subprocess.run(command, shell=True)

    deploy_core_server(wallet)
    sleep(10)
                                                
