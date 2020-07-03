from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.functions.text import print_result
import os

def main():
    os.environ['NET_TEXTFSM'] = './ntc-templates/templates'
    nr = InitNornir(config_file="./config.yaml")
    aggresult = nr.run(task=netmiko_send_command, command_string="show ip interface brief", use_textfsm=True)
    print_result(aggresult)

if __name__ == "__main__":
    main()

