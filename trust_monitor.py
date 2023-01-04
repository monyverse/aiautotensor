import bittensor as bt
import yaml
import time
import subprocess

def main():
    while True:
        with open('config.yaml', 'r') as file:
            machs = yaml.safe_load(file)

        for machine_id in machs.keys():
            machine_config = machs[machine_id]
            for gpu_index, gpu_config in enumerate(machine_config):
                wallet = bt.wallet(name=(gpu_config['wallet']), path="auto_wallets/",
                                   hotkey=str(gpu_config['keyfile']))
                st = bt.subtensor(network="nakamoto")
                neuron = st.neuron_for_wallet(wallet)
                print(neuron.trust)
                if neuron.trust < .5:
                    command = f"curl -H \"Content-Type: application/json\" -d '{{\"content\": \"@here The {wallet.hotkey_str} key on {machine_id} has a trust score of {neuron.trust}\"}}' \"<insert discord API key here>\""
                    print(command)
                    subprocess.run(command, shell=True)
        time.sleep(300)

main()
