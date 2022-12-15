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
def deploy_core_server(vr_threshold: int = 1000, vram_used: list = []):
    """Deploys a bittensor core_server on a GPU with VRAM usage below the specified threshold.
       Args:
               vr_threshold: VRAM threshold below which a bittensor core_server is deployed.
               vram_used: List of VRAM usage values, in bytes.
                """
    if subtensor is None:
        subtensor = bt.subtensor()
    return subtensor.is_hotkey_registered(wallet.hotkey.ss58_address)

# Define the deploy_core_server function
def deploy_core_server(vr_threshold: int = 1000, vram_used: list = []):
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

        # If the VRAM usage is below the threshold and a core_server has not been deployed yet, deploy a bittensor core_server
        if vram_used < vr_threshold:
            # Get the index of the GPU with VRAM usage below the threshold
            gpu_index = output.split(b'\n').index(line)

            print(f"Deploying bittensor core_server on GPU with {vram_used} MB of VRAM (GPU index: {gpu_index})")
            # Set the current GPU as the active device
            torch.cuda.set_device(gpu_index)

            command = "pm2 start ~/.bittensor/bittensor/bittensor/_neuron/text/core_validator/main.py --name Eugene --time --interpreter python3 -- --logging.debug --subtensor.network nobunaga --neuron.device cuda:{} --wallet.name test --wallet.hotkey 0".format(gpu_index)
            # Run the command in the command line
            subprocess.run(command, shell=True)

            # Set the done flag to True
            return




            # config = None
            # dataset = bt.dataset()
            # subtensor = bt.subtensor(network = "nakamoto")
            # wallet = bt.wallet(name="Nicomachus", hotkey="Eugene")
            # axon = bt.axon(port = 8000, wallet = wallet)
            # metagraph = bt.metagraph()
            # template = bt.neurons.core_server.neuron(config = config, subtensor = subtensor, wallet = wallet, axon = axon, metagraph = metagraph).run()
            # template = bt.neurons.core_validator.neuron(config = config, subtensor = subtensor, wallet = wallet, axon = axon, metagraph = metagraph).run()
        pass

# Define the create_array() function
def create_array():
    # Get the number of GPUs on the system
    num_gpus = torch.cuda.device_count()

    # Create a list of numbers from 0 to num_gpus (inclusive)
    range_array = list(range(num_gpus))

    # Concatenate the elements of the range_array list into a single string
    # with a space between each number
    range_string = ' '.join(str(x) for x in range_array)

    # Return the resulting string
    return range_string


# Get the number of GPUs on the system
num_gpus = torch.cuda.device_count()

# Define a list of wallets
wallets = []
for i in range(num_gpus):
    # Create a new wallet object for each GPU
    wallet = bt.wallet(name="test", hotkey=str(i))
    wallets.append(wallet)

    # Check if the wallet is registered
    while not is_registered(wallet):
        # Create a subtensor object for the current GPU
        deploy_core_server()
        break
        # if not is_registered(wallet):
        # Register the wallet using the current GPU
        #range_string = create_array()

        # import pdb
        # pdb.set_trace()

        #command = "btcli register --subtensor.network nobunaga --wallet.name {} --wallet.hotkey {} --cuda --cuda.dev_id {} --cuda.TPB 512 --cuda.update_interval 250_000 --no_prompt".format(wallet.name, wallet.hotkey_str, range_string)

        # Run the command in the command line
        #subprocess.run(command, shell=True)
        #break
