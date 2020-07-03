from nornir import InitNornir

def my_task(task):
    print(task.host.hostname)
    return f"This is a nornir task exec in {task.host.hostname}"

def main():
    #nr = InitNornir(core={"num_workers": 1})
    nr = InitNornir(config_file="./config.yaml")
    aggresult = nr.run(task=my_task)
    multiresult = aggresult['r1']
    r = multiresult[0]
    #ipdb.set_trace()

if __name__ == "__main__":
    main()
