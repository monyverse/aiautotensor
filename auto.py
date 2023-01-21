import os
import subprocess
from time import sleep
import bittensor as bt
import torch
import yaml
from rich.prompt import Confirm, Prompt, PromptBase
import nvidia_smi


MACHINE = Prompt.ask(
    "Which machine id is this?"
)    
os.environ["MACHINE_ID"] = MACHINE
NOTIF1 = Prompt.ask(
    "Would you like to cut TPB for registration if a GPU is serving a model?",
    choices=["yes", "no"],
    default="yes",
)
if NOTIF1 == "yes":
    TPB = Prompt.ask(
        "What would you like the TPB to be for GPUs that are serving?",
        choices=["0", "64", "128", "256"],
        default="256",
)   
NOTIF2 = Prompt.ask(
    "Would you like to turn on discord notifications?",
    choices=["yes", "no"],
    default="yes",
)
if NOTIF2 == "yes":
    API_KEY = Prompt.ask("Enter your discord api key", default="")


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


def gpu_is_used(i):
    handle = nvidia_smi.nvmlDeviceGetHandleByIndex(i)
    info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)

    return (info.used/info.total) > 0.03


def check_is_running(proc_name: str) -> bool:
    pm2_output = subprocess.check_output(["pm2", "id", proc_name])
    return len(pm2_output) > 3


def kill_pm2(proc_name: str):
    os.system(f"pm2 delete {proc_name}")


def make_proc_name(gpu_config, wallet) -> str:
    return f"{gpu_config['name']}_{wallet.hotkey_str}"


# Define the deploy_core_server function
def deploy_core_server(gpu_index, gpu_config, wallet: "bt.Wallet"):

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

with open("config.yaml", "r") as file:
    machs = yaml.safe_load(file)

if os.getenv("MACHINE_ID") is None:
    os.environ["MACHINE_ID"] = MACHINE
assert os.getenv("MACHINE_ID") in machs.keys()


while True:
    for machine_id in machs.keys():
        machine_config = machs[machine_id]
        for gpu_index, gpu_config in enumerate(machine_config):
            # Create a new wallet object for each GPU
            wallet = bt.wallet(
                name=(gpu_config["wallet"]),
                path="auto_wallets/",
                hotkey=str(gpu_config["keyfile"]),
            )
            # Check if the wallet is registered
            if not is_registered(
                wallet, network=gpu_config["network"]
            ):
                expected_proc_name = make_proc_name(
                    gpu_config=gpu_config, wallet=wallet
                )
                if check_is_running(expected_proc_name):
                    kill_pm2(expected_proc_name)
                    if NOTIF == "yes":
                        command = f'curl -H "Content-Type: application/json" -d \'{{"content": "@here The {wallet.hotkey_str} key on {machine_id} has been deregistered!"}}\' "{API_KEY}"'
                        print(command)
                        subprocess.run(command, shell=True)

            def make_command(cuda_devs: str, tpb: int):
                command = (
                    f"btcli register "
                    f"--subtensor.network {gpu_config['network']} "
                    f"--wallet.name {wallet.name} "
                    f"--wallet.hotkey {wallet.hotkey_str} "
                    f"--wallet.path auto_wallets/ "
                    f"--cuda "
                    f"--cuda.dev_id {cuda_devs} "
                    f"--cuda.TPB {tpb} "
                    f"--cuda update_interval 70_000 "
                    f"--no_prompt "
                )

                return command

            while not is_registered(wallet, network=gpu_config["network"]):
                sleep(30)

                nvidia_smi.nvmlInit()
                deviceCount = nvidia_smi.nvmlDeviceGetCount()

                used_gpus = []
                unused_gpus = []
                for i in range(deviceCount):
                    if gpu_is_used(i):
                        used_gpus.append(str(i))
                    else:
                        unused_gpus.append(str(i))
                print("Used GPUs: ", " ".join(used_gpus))
                print("Unused GPUs: ", " ".join(unused_gpus))
                command1 = make_command(" ".join(unused_gpus), 512)
                command2 = make_command(" ".join(used_gpus), TPB)
                print(command1)
                print(command2)
                proc1 = subprocess.Popen(command1.split())
                proc2 = subprocess.Popen(command2.split())

                for proc in (proc1, proc2): proc.wait()

                if NOTIF == "yes" and MACHINE == "machine1":
                    command = f'curl -H "Content-Type: application/json" -d \'{{"content": "@here The {wallet.hotkey_str} key on {machine_id} has been registered!"}}\' "{API_KEY}"'
                    subprocess.run(command, shell=True)


            if machine_id == os.getenv("MACHINE_ID"):
                deploy_core_server(gpu_index, gpu_config, wallet)

            sleep(10)
