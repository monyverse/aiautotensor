import torch
import subprocess
import cubit
import bittensor as bt


# Check if registerred function
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

# Get the current VRAM usuage of each GPU and define a threshold
def deploy_core_server(vr_threshold: int = 4800, vram_used: list = []):
    """Deploys a bittensor core_server on a GPU with VRAM usage below the specified threshold.
       Args:
               vr_threshold: VRAM threshold below which a bittensor core_server is deployed.
               vram_used: List of VRAM usage values, in bytes.
       """
    # Use the nvidia-smi to get the VRAM usage of each GPU
    output = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"])

    # Parse the output to get the VRAM usage of each GPU
    for line in output.split(b'\n'):
        # Skip empty lines
        if line == b'':
            continue

        # Convert the VRAM usuage from bytes to MB
        vram_used = int(line.strip())

        # If the VRAM usage is below the threshold, deploy a Miner
        if vram_used < vr_threshold:
            print(f"Deploying bittensor core_server on GPU with {vram_used} MB of VRAM")
            # Load the core_server model
            config = None
            # dataset = bt.dataset()
            subtensor = bt.subtensor(network = "<>")
            wallet = bt.wallet(name="<>", hotkey="<>")
            axon = bt.axon(port = <>, wallet = wallet)
            metagraph = bt.metagraph()
            
            # RUN SERVERS OR VALIDATORS. UNCOMMENT
            
            # template = bt.neurons.core_server.neuron(config = config, subtensor = subtensor, wallet = wallet, axon = axon, metagraph = metagraph).run()
            # template = bt.neurons.core_validator.neuron(config = config, subtensor = subtensor, wallet = wallet, axon = axon, metagraph = metagraph).run()
            pass

# Create an array of the total number of GPUs
def create_array():
    # Get the number of GPUs
    num_gpus = torch.cuda.device_count()

    # Create a list of numbers from 0 to num_gpus
    range_array = list(range(num_gpus))

    # Concatenate the elements of the range_array list into a single string with a space between each number
    range_string = ' '.join(str(x) for x in range_array)

    # Return the string
    return range_string


# Get the number of GPUs
num_gpus = torch.cuda.device_count()

# Define a list of wallets
wallets = []
for i in range(num_gpus):
    # Create a new wallet object for each GPU
    wallet = bt.wallet(name="<>", hotkey="<>")
    wallets.append(wallet)

    # Check if the wallet is registered
    if not is_registered(wallet):
        # Create a subtensor object for the current GPU
        subtensor = bt.subtensor()

        # Register the wallet using the current GPU
        range_string = create_array()

        # import pdb ### debugging
        # pdb.set_trace() ### debugging
        
        #registration command 
        command = "btcli register --subtensor.network local --wallet.name {} --wallet.hotkey {} --cuda --cuda.dev_id {} --cuda.TPB 512 --cuda.update_interval 250_000 --no_prompt".format(wallet.name, wallet.hotkey_str, range_string)

        # Run the command in the command line
        subprocess.run(command, shell=True)
    else:
        deploy_core_server()
