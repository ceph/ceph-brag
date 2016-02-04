
# coding: utf-8

# # Create JSON files from Ceph tests data in CSV format
# 
# This notebook reads a CSV file with one Ceph test per row, and produces one JSON file for each test, using the proposed JSON format. This notebook is intended only for having some JSON files to test the production of the Ceph-brag dashboard. Please, note that the CSV file may include incorrect data. In particular, date and cluster_uuid are fake.

# First of all, read the csv file into a Pandas dataframe (just because it is convenient to later produce the JSON files).

# In[23]:

import pandas as pd

tests_4ms_df = pd.read_csv("ceph-tests-data-4ms.csv")
tests_4kr_df = pd.read_csv("ceph-tests-data-4kr.csv")


# The function create_description produces a dictionary ready to be exported as a JSON file. It takes as arguments the data for one test (which correspons to one row in the CSV file), and an integer (which corresponds to the position of the row in the CSV file, starting with 0). The integer is used only for helping in producing the date (we don't have real dates in the CSV file). The data specific for the benchmarks is not produced here.

# In[24]:

from collections import OrderedDict
def create_description (test, order):
    """Fill a description dictionary from information in a dataframe row."""
    
    description = OrderedDict()
    description["information"] = {
        "cluster_uuid": "5e4eeae5-edf4-4d53-8ed5-5675207f9a35",
        "date": "2014-05-" + "{0:0=2d}".format(order+1) + "T20:00:34",
        "submitter": {
            "person": test["person"],
            "company": test["company"]
        }
    }
    description["platform"] = {
        "osds": test["osd_test"],
        "osd_servers": test["osd_servers_test"],
        "osd_devices": test["osd_devices_test"],
        "osd_media": test["osd_media"],
        "cost_raw_tb": test["cost_raw_tb"],
        "ceph_data_protection": test["ceph_data_protection"],
        "cost_usable_tb": test["cost_usable_tb"],
        "v_fio": "2.2.13",
        "v_sysbench": "0.5",
        "v_radosbench": "9.2.0",
        "v_collectl": "4.0.2",
    }
    description["osd_servers"] = {
        "server_vendor": test["vendor"],
        "server_model": test["model"],
        "3_5_hdds_for_osds": test["3_5_hdds"],
        "2_5_hdds_for_osds": test["2_5_hdds"],
        "2_5_ssds_for_osds": test["2_5_ssds"],
        "nvme_for_osds": test["pcie_nvm"],
        "journal_model": test["journal_model"],
        "CPU": test["cpu"],
        "CPU_sockets": test["cpu_sockets"],
        "RAM_GB": test["ram_ddr"],
        "HBA/RAID": test["controller"],
        "HBA/RAID_model": test["hba_raid_model"],
        "Network_Interface": test["network_interface"],
        "v_OS": test["os_version"],
        "v_kernel": test["kernel"]
    }
    description["pools"] = [
        {
            "pool_id": 0,
            "pool_name": "data",
            "pool_pgpnum": 512,
            "pool_size": 2
        },
        {
            "pool_id": 32,
            "pool_name": "ssd",
            "pool_pgpnum": 512,
            "pool_size": 1
        }
    ]
    description["ceph"] = {
        "v_ceph": test["ceph_version"],
        "pg_count": test["ceph_groups"],
    }
    description["network"] = {
        "pub_network": test["net_public"],
        "cluster_network": test["net_cluster"]
    }
    description["clients"] = {
        "client_node_count": test["client_nodes"],
        "Client_OS": test["client_os"],
        "client_vm_count": test["client_vms"],
        "ceph_client": test["ceph_client"]
    }
    description["load"] = {
        "load_test_util": test["load_utility"],
        "IO_queue_depth": test["load_io_queue"]
    }
    if test["load_cbt"] == "Y":
        description["load"]["CBT"] = 1
    else:
        description["load"]["CBT"] = 0
    description["publication"] = {
        "publication_url": test["link"]
    }
    if test["published"] == "Y":
        description["load"]["published"] = 1
    else:
        description["load"]["published"] = 0
    description["notes"] = {
        "observations": test["observations"]
    }
    return description


# create_benchmarks_4ms is a function for creating the benchmarks property of a description, when that information relates to 4M Sequential tests.

# In[25]:

def create_benchmarks_4ms (test):
    benchmarks = [
        {
            "suite": "CBT_Throughput-optimized",
            "kind": "4M Sequential Read",
            "mbsec_osd_device": test["4MSR_mbsec_osd_device"],
            "cost_usable_tb_mbsec": test["4MSR_cost_usable_tb_mbsec"],
            "mbsec_cluster": test["4MSR_mbsec_cluster"],
            "avg_latency": test["4MSR_latency_avg"],
            "95th_latency": test["4MSR_latency_95"]
        },
        {
            "suite": "CBT_Throughput-optimized",
            "kind": "4M Sequential Write",
            "mbsec_osd_device": test["4MSW_mbsec_osd_device"],
            "cost_usable_tb_mbsec": test["4MSW_cost_usable_tb_mbsec"],
            "mbsec_cluster": test["4MSW_mbsec_cluster"],
            "avg_latency": test["4MSW_latency_avg"],
            "95th_latency": test["4MSW_latency_95"]
        }
    ]
    return benchmarks


# create_benchmarks_4kr is a function for creating the benchmarks property of a description, when that information relates to 4K Random tests.

# In[26]:

def create_benchmarks_4kr (test):
    benchmarks = [
        {
            "suite": "IOPS-optimized",
            "kind": "4K Random Read",
            "mbsec_osd_device": test["4KRR_IOPS_OSD"],
            "cost_usable_tb_mbsec": test["4KRR_media_cost_IOP"],
            "mbsec_cluster": test["4KRR_IOPS_cluster"],
            "avg_latency": test["4KRR_latency_avg"],
            "95th_latency": test["4KRR_latency_95"]
        },
        {
            "suite": "IOPS-optimized",
            "kind": "4K Random Write",
            "mbsec_osd_device": test["4KRW_IOPS_OSD"],
            "cost_usable_tb_mbsec": test["4KRW_media_cost_IOP"],
            "mbsec_cluster": test["4KRW_IOPS_cluster"],
            "avg_latency": test["4KRW_latency_avg"],
            "95th_latency": test["4KRW_latency_95"]
        }
    ]
    return benchmarks


# Function file_name produces a file name from the date and cluster_uuid in the description of a test.

# In[27]:

def file_name (description):
    """Produce the file name for a test description"""

    name = description["information"]["date"]
    name = name.replace("T", "_")
    name = name + "_" + description["information"]["cluster_uuid"]
    return name


# Now, the rest is simple. Just loop through all rows in the dataframe, produce a description (dictionary ready to be exported as JSON) for each of them, produce a file name for each of them, and then write the dictionary to the file.

# In[28]:

import json

def create_json (df, benchmark_func, previous_id):
    id = previous_id
    for index, row in df.iterrows(): 
        id = id + 1
        description = create_description(row, id)
        description["benchmarks"] = benchmark_func(row)
        name = file_name(description) + ".json"
        with open(name, 'w') as f:
            print(name)
            json.dump(dict(description), f, ensure_ascii=False, indent=2)
    return (id)

id = 0
id = create_json(tests_4ms_df, create_benchmarks_4ms, id)
id = create_json(tests_4kr_df, create_benchmarks_4kr, id)


# In[ ]:



