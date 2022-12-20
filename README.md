# autominer
automated bittensor mining

Recommended:

Setup am ssh config:

```bash
Host <>
				HostName <IP>
				Port <>
				User <>

Host <>
				HostName <IP>
				Port <>
				User <>
```

Step 1:

git clone [https://github.com/quac88/autominer/tree/main](https://github.com/quac88/autominer/tree/main)

Step 2:

Open the directory:

```bash
cd ~/.autominer
```

Step 2: 

Configure the yaml:

Each “-” represents a GPU

```bash
machine1:
  -
    name: "a"
    model: "gpt2"
    port: 8091
    keyfile: 0
    wallet: "test"
  -
    name: "b"
    model: "gpt-neo-125M"
    port: 8093
    keyfile: 1
    wallet: "test"
  -
    name: "c"
    model: "gpt-neo-125M"
    port: 8094
    keyfile: 2
    wallet: "test"
  -
    name: "d"
    model: "gpt-neo-125M"
    port: 8095
    keyfile: 3
    wallet: "test"
machine2:
  -
    name: "i"
    model: "gpt2"
    port: 8096
    keyfile: 4
    wallet: "test"
  -
    name: "j"
    model: "gpt-neo-125M"
    port: 8097
    keyfile: 5
    wallet: "test"
  -
    name: "k"
    model: "gpt-neo-125M"
    port: 8098
    keyfile: 6
    wallet: "test"
  -
    name: "l"
    model: "gpt-neo-125M"
    port: 8099
    keyfile: 7
    wallet: "test"
```

The configuration above represent mining architecture for two machine each with 4 GPUs.

Step 2:

Create Keys:

python3 create_keys.py

```python
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
```

Step 3: 

Copy keys to each machine:

```bash
scp -r autominer <user>
```

Step 4:

Install PM2 & TMUX:

```bash
sudo apt update
sudo apt upgrade
sudo apt install npm -y
sudo npm install pm2@latest -g
sudo apt install tmux
```

Step 5:

Open TMUX:

```bash
tmux
```

Step 6: 

Run auto miner:

  ```
  
