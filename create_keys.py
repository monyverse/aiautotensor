import bittensor as bt
import yaml
import subprocess

with open('config.yaml', 'r') as file:
    machs = yaml.safe_load(file)

for machine_id in machs.keys():
    machine_config = machs[machine_id]
    for gpu_index, gpu_config in enumerate(machine_config):
        wallet = bt.wallet(name=(gpu_config['wallet']), hotkey=str(gpu_config['keyfile']))
        # Start the btcli new_hotkey command in a separate process
        command = (
            f"btcli new_hotkey --wallet.name {wallet.name} " 
            f"--wallet.hotkey {wallet.hotkey_str} "
            f"--wallet.path auto_wallets/ "
            f"--no_prompt"
        )
        print(command)
        subprocess.run(command, shell=True)
