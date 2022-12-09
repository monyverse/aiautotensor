# Hotkey for loop
# Loop through and create 10 hotkeys
for i in range(10):
    # Start the btcli new_hotkey command in a separate process
    process = subprocess.Popen(["btcli", "new_hotkey"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    # Write input and read output
    output, _ = process.communicate(input=f"test\n{i}\n".encode())

    # Print the output
    print(output.decode())

# Questions
# 1. If hotkey named x exists, skip to next integer
