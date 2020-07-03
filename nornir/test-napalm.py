from nornir import InitNornir
from nornir.plugins.tasks.networking import napalm_get
from nornir.plugins.functions.text import print_result

def main():
    nr = InitNornir(config_file="./config.yaml")
    #aggresult = nr.run(task=napalm_get, getters=["config"])
    aggresult = nr.run(task=napalm_get, getters=["config","lldp_neighbors"], getters_options={"config": {"retrieve": "running"}})
    #aggresult = nr.run(task=napalm_get, getters=["facts","lldp_neighbors","arp_table"])
    print_result(aggresult)

if __name__ == "__main__":
    main()

