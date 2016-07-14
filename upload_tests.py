#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## Copyright (C) 2015 Bitergia
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Authors:
##   Jesus M. Gonzalez-Barahona <jgb@bitergia.com>
##

description = """
Read JSON files, each corresponding to a Ceph test, and upload to ElasticSearch.

Example:

python3 upload_tests.py --dir bootstrapping/ \
  --elasticsearch http://elastic-ceph.bitergia.com:80 ceph-tests --esauth ceph XXX
"""

import argparse
import os
import json
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, String, Date, Integer, Float, Object, Index

def parse_args ():
    """
    Parse command line arguments

    """
    parser = argparse.ArgumentParser(description = description)
    parser.add_argument("--dir",
                        help = "Directory with test files")
    parser.add_argument("--files", nargs='+',
                        help = "Test files (paths)")
    parser.add_argument("--elasticsearch", nargs=2,
                        help = "Url of elasticsearch, and index to use " + \
                        "(eg: http://localhost:9200 project)")
    parser.add_argument("--esauth", nargs=2, default = None,
                        help = "Authentication to access ElasticSearch" + \
                        "(eg: user password)")
    parser.add_argument("--delete", action='store_true',
                        help = "Delete index before adding tests")
    parser.add_argument("--dry", action='store_true',
                        help = "Run a dry test")
    parser.set_defaults(dry=False)
    args = parser.parse_args()
    return args

def read_files (files):
    """
    Read test files, given a list with their paths

    :param files: list of files
    :returns: list with the corresponding tests

    """

    tests = {}
    for file in files:
        with open(file) as json_file:
            data = json.load(json_file)
            date = data["information"]["date"]
            uuid = data["information"]["cluster_uuid"]
            name = date + "_" + uuid
            tests[name] = data
    return tests
    
def read_dir (dir):
    """
    Read test files from directory dir.

    :param dir: directory with test files

    :returns: a list with all the tests

    """

    files = [os.path.join(dir, file) for file in os.listdir(path = dir)]
    files = [file for file in files
                if os.path.isfile(file) and
                    os.path.splitext(file)[-1].lower() == ".json"]
    tests = read_files(files)
    return tests

Results = Object(
    properties = {
        "mbsec_osd_device": Integer(),
        "cost_usable_tb_mbsec": Float(),
        "mbsec_cluster": Float(),
        #"latency_avg": Float()
        })

class Test(DocType):
    Id = String(index='not_analyzed')
    Suite = String(index='not_analyzed')
    Config = String(index='not_analyzed')
    Test_no = Integer()
    Author = String(index='not_analyzed')
    Company = String(index='not_analyzed')
    OSD_Servers = Integer()
    OSDs = Integer()
    OSD_Devices = Integer()
    OSD_Media = String(index='not_analyzed')
    #cost_raw_tb = Float()
    Data_Protection = String(index='not_analyzed')
    Suite = String(index='not_analyzed')
    #cost_usable_tb = Float()

    class Meta:
        index = 'ceph-tests'

class Test_Sequential(Test):
    Seq_Read_4M = Results
    Seq_Write_4M = Results

class Test_Random(Test):
    Rand_Read_4K = Results
    Rand_Write_4K = Results

def benchmark_results (benchmark):
    """Produce a Seq_Results object from a benchmark dictionary.

    """
    results = {}
    results["mbsec_osd_device"] = benchmark["mbsec_osd_device"]
    if "cost_usable_tb_mbsec" in results:
        results["cost_usable_tb_mbsec"] = float(benchmark["cost_usable_tb_mbsec"])
    results["mbsec_cluster"] = float(benchmark["mbsec_cluster"])
    if "latency_avg" in results:
        results["latency_avg"] = float(benchmark["latency_avg"])
    return results

def upload_elasticsearch (tests, es_server, es_auth, delete=False, dry=False):
    """Upload to ElasticSearch.

    :param tests: dictionary with tests
    :param es_server: ElasticSearch data, list ["host:port", "index"]
    :param es_auth: ElasticSearch auth data, list ["user", "passwd"]
    :param dry: dry test (do not upload data to ElasticSearch)

    """

    if not dry:
        connections.create_connection(hosts=[es_server[0]],
                                      http_auth=[es_auth[0], es_auth[1]])
        index = Index (es_server[1])
        if delete:
            index.delete(ignore = 404)
        Test_Sequential.init()
    cont = 0
    for name, data in tests.items():
        cont = cont + 1
        config = str(data["platform"]["osds"]) + "/" \
            + data["platform"]["osd_media"] + "/" \
            + data["platform"]["ceph_data_protection"]
        for benchmark in data["benchmarks"]:
            if benchmark["suite"] == "CBT_Throughput-optimized":
                suite = "CBT Throughput optimized"
                print("Found suite: {}".format(suite))

                if benchmark["kind"] == "4M Sequential Read":
                    Seq_Read_4M = benchmark_results (benchmark)
                    fourMSR_mbsec_osd_device = benchmark["mbsec_osd_device"]
                    fourMSR_mbsec_cluster = float(benchmark["mbsec_cluster"])
                    fourMSR_latency_avg = benchmark["avg_latency"]
                elif benchmark["kind"] == "4M Sequential Write":
                    Seq_Write_4M = benchmark_results (benchmark)
                    fourMSW_mbsec_osd_device = benchmark["mbsec_osd_device"]
                    fourMSW_mbsec_cluster = float(benchmark["mbsec_cluster"])
                    fourMSW_latency_avg = benchmark["avg_latency"]
            elif benchmark["suite"] == "IOPS-optimized":
                suite = "IOPS optimized"
                print("Found suite: {}".format(suite))
                if benchmark["kind"] == "4K Random Read":
                    Rand_Read_4K = benchmark_results (benchmark)
                elif benchmark["kind"] == "4K Random Write":
                    Rand_Write_4K = benchmark_results (benchmark)
            else:
                print("Warning: unknown suite: {} (ignoring)".format(benchmark["suite"]))
                suite = ""
        if suite == "CBT Throughput optimized":
            test = Test_Sequential (
                 meta={'id': name},
                 Id = name,
                 Suite = suite,
                 Config = config,
                 Test_no = cont,
                 Author = data["information"]["submitter"]["person"],
                 Company = data["information"]["submitter"]["company"],
                 OSD_Servers = data["platform"]["osd_servers"],
                 OSDs = data["platform"]["osds"],
                 OSD_Devices = data["platform"]["osd_devices"],
                 OSD_Media = data["platform"]["osd_media"],
                 #cost_raw_tb = data["cost_raw_tb"],
                 Data_Protection = data["platform"]["ceph_data_protection"],
                 #cost_usable_tb = data["cost_usable_tb"],
                )
            test.Seq_Read_4M = Seq_Read_4M
            test.Seq_Write_4M = Seq_Write_4M
        elif suite == "IOPS optimized":
            test = Test_Random (
                 meta={'id': name},
                 Id = name,
                 Suite = suite,
                 Config = config,
                 Test_no = cont,
                 Author = data["information"]["submitter"]["person"],
                 Company = data["information"]["submitter"]["company"],
                 OSD_Servers = data["platform"]["osd_servers"],
                 OSDs = data["platform"]["osds"],
                 OSD_Devices = data["platform"]["osd_devices"],
                 OSD_Media = data["platform"]["osd_media"],
                 #cost_raw_tb = data["cost_raw_tb"],
                 Data_Protection = data["platform"]["ceph_data_protection"],
                 #cost_usable_tb = data["cost_usable_tb"],
                )
            test.Rand_Read_4K = Rand_Read_4K
            test.Rand_Write_4K = Rand_Write_4K

        if suite != "":
            print ("Test")
            print(test)
            if not dry:
                test.save()

if __name__ == "__main__":

    args = parse_args()
    if args.dir:
        tests = read_dir(args.dir)
    elif args.files:
        tests = read_files(args.files)
    else:
        print("Error: specify --dir or --files")
        exit()
    print(tests)
    print()
    upload_elasticsearch(tests, args.elasticsearch, args.esauth,
                         delete=args.delete, dry=args.dry)
