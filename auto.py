import torch
import subprocess
import cubit
import bittensor as bt

# Define the is_registered() function
def is_registered(wallet, subtensor: 'bt.Subtensor' = None) -> bool:
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
        subtensor = bt.subtensor()
    return subtensor.is_hotkey_registered(wallet.hotkey.ss58_address)

# Define the deploy_core_server function
def deploy_core_server(vr_threshold: int = 4800, vram_used: list = []):
    """Deploys a bittensor core_server on a GPU with VRAM usage below the specified threshold.
       Args:
               vr_threshold: VRAM threshold. If below threshold, deploy a Server
               vram_used: List of VRAM usage values (bytes)
       """
    # Check nvidia-smi to get VRAM usage per GPU
    output = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"])

    # Parse the output to get the VRAM usage of each GPU
    for line in output.split(b'\n'):
        # Skip empty lines
        if line == b'':
            continue

        # Convert VRAM usage from bytes to MB
        vram_used = int(line.strip())

        # If the VRAM usage < threshold, deploy core_server
        if vram_used < vr_threshold:
            print(f"Deploying bittensor core_server on GPU with {vram_used} MB of VRAM")
            # Run core_server
            config = bt.config()
            subtensor = bt.subtensor(network = "nakamoto")
            wallet = bt.wallet()
            axon = bt.axon()
            metagraph = bt.metagraph()

            # Run the core server
            template = bt.neurons.core_server.neuron(config, subtensor, wallet, axon, metagraph).run()
            pass

# Create an array for GPUs
def create_array():
    # Get the number of GPUs
    num_gpus = torch.cuda.device_count()

    # Create a list of numbers from 0 to num_gpus
    range_array = list(range(num_gpus))

    # Concatenate the elements of the range_array list into a string with a space between each number
    range_string = ' '.join(str(x) for x in range_array)

    return range_string


# Get the number of GPUs
num_gpus = torch.cuda.device_count()

# Define a list of wallets
wallets = []
for i in range(num_gpus):
    wallet = bt.wallet(name="<>", hotkey="<>")
    wallets.append(wallet)
    
    # Check if the wallet is registered
    if not is_registered(wallet):
        # Create a subtensor object for the current GPU
        subtensor = bt.subtensor()

        # Register the wallet
        range_string = create_array()
        command = "btcli register --subtensor.network local --wallet.name {} --wallet.hotkey {} --cuda --cuda.dev_id {} --cuda.TPB 512 --cuda.update_interval 70_000 --no_prompt".format(wallet.name, range_string)

        # Run on command line
        subprocess.run(command, shell=True)
    else:
        # Run a Server
        deploy_core_server()
