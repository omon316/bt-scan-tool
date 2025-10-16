import sys
import threading
import time
import subprocess
#from bluetooth_scan import scan_and_store, manual_scan_and_send, scan_bluetooth_devices, store_device, format_device_info, log_device, get_device_index
from bluetooth_scan import scan_and_store, manual_scan_and_send, scan_bluetooth_devices, store_device, format_device_info, log_device, get_device_index
from telegram_report import send_initial_notification, send_report


running = False
global_index_counter = 1  # Ensure this is consistent with bluetooth_scan.py

def start_program():
    global running
    if running:
        print("\033[91mProgram is already running!\033[0m")
        return
    running = True
    send_initial_notification()
    threading.Thread(target=program_loop).start()
    print("\033[92mProgram started successfully!\033[0m")

def stop_program():
    global running
    if not running:
        print("\033[91mProgram is not running!\033[0m")
        return
    running = False
    print("\033[93mProgram stopped!\033[0m")

def program_loop():
    global running
    while running:
        devices = scan_and_store()
        send_report(devices)
        time.sleep(900)  # Wait for 15 minutes

def show_status():
    if running:
        print("\033[92mProgram is running!\033[0m")
    else:
        print("\033[91mProgram is stopped!\033[0m")

def view_logs():
    try:
        with open("logs/bluetooth_scan.log", "r") as file:
            print(file.read())
    except FileNotFoundError:
        print("\033[91mNo logs available!\033[0m")

def live_mode():
    try:
        while True:
            devices = scan_bluetooth_devices()
            for addr, name in devices:
                if store_device(addr, name):
                    device_index = get_device_index(addr)  # Get the unique index for this MAC address
                    device_info = format_device_info(device_index, addr, name)
                    print(f"\033[94m{device_info}\033[0m")
                    log_device(device_info)  # Log the device info
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\033[93mExiting live mode.\033[0m")


def send_manual_message():
    log_file_path = "logs/bluetooth_scan.log"
    try:
        with open(log_file_path, "r") as log_file:
            log_content = log_file.read()
            if log_content:
                from telegram_report import send_telegram_message
                success = send_telegram_message(log_content)
                if success:
                    print("\033[92mLog file content sent successfully via Telegram!\033[0m")
                else:
                    print("\033[91mFailed to send log file content via Telegram.\033[0m")
            else:
                print("\033[91mLog file is empty, nothing to send.\033[0m")
    except FileNotFoundError:
        print("\033[91mLog file not found!\033[0m")


def show_help():
    print("""
    Available commands:
    - start: Start the Bluetooth scanning program
    - stop: Stop the program
    - status: Show if the program is running
    - logs: View the log file
    - live: Enter live mode to see scan results in real-time
    - send: Manually send a Telegram message with current detected devices
    - select_receiver: Select the Bluetooth receiver to use
    - help: Show this help menu
    - exit: Exit the CLI
    """)

def start_cli():
    global selected_receiver

    while True:
        command = input("\033[96mEnter command (type 'help' for list of commands): \033[0m").strip().lower()
        if command == "start":
            start_program()
        elif command == "stop":
            stop_program()
        elif command == "status":
            show_status()
        elif command == "logs":
            view_logs()
        elif command == "live":
            live_mode()
        elif command == "send":
            send_manual_message()
        elif command == "select_receiver":
            selected_receiver = select_bluetooth_receiver()
        elif command == "help":
            show_help()
        elif command == "exit":
            if running:
                stop_program()
            sys.exit(0)
        else:
            print("\033[91mUnknown command!\033[0m")

def list_bluetooth_receivers():
    result = subprocess.run(["hcitool", "dev"], stdout=subprocess.PIPE)
    devices = result.stdout.decode().splitlines()[1:]  # Skip the first line (header)
    return [line.split()[1] for line in devices]  # Extract the MAC addresses

def select_bluetooth_receiver():
    receivers = list_bluetooth_receivers()
    if not receivers:
        print("No Bluetooth receivers found.")
        return None

    print("Select a Bluetooth receiver:")
    for i, receiver in enumerate(receivers, 1):
        print(f"{i}. {receiver}")

    choice = int(input("Enter the number of the receiver to use: ").strip())
    if 1 <= choice <= len(receivers):
        return receivers[choice - 1]
    else:
        print("Invalid choice. Please try again.")
        return None

# Add the Bluetooth receiver selection function to your start sequence if needed.
selected_receiver = select_bluetooth_receiver()



