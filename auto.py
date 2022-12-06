import torch
import subprocess
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

# Create a new wallet object
wallet = bt.wallet(name="<>", hotkey="<>")

# Define a list of wallets
wallets = [wallet]
for wallet in wallets:
    # Check if the wallet is registered
    if not is_registered(wallet):
        # Register the wallet using the specified GPUs
        wallet.register()
    else:
        def deploy_core_server(vr_threshold: int, vram_used: list):

# Define the deploy_core_server function
def deploy_core_server(vr_threshold: int, vram_used: list):
    """Deploys a bittensor core_server on a GPU with VRAM usage below the specified threshold.
       Args:
               vr_threshold: VRAM threshold below which a bittensor core_server is deployed.
               vram_used: List of VRAM usage values, in bytes.
       """
    # Use the nvidia-smi command to get the VRAM usage of each GPU
    output = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"])

    # Parse the output to get the VRAM usage of each GPU
    for line in output.split(b'\n'):
        # Skip empty lines
        if line == b'':
            continue

        # Convert the VRAM usage from bytes to MiB
        vram_used = int(line.strip())

        # If the VRAM usage is below the threshold, deploy a bittensor core_server
        if vram_used < vr_threshold:
            print(f"Deploying bittensor core_server on GPU with {vram_used} MB of VRAM")
            # Load the core_server model
            model = bt.neurons.core_server.server()

            # Create a config object
            config = bt.config()

            # Sync the metagraph
            metagraph = bt.metagraph().load().sync().save()

            # Create a new Subtensor object
            subtensor = bt.subtensor(config=config, network="nakamoto")

            # Start the server
            subtensor.serve(model=model, metagraph=metagraph)