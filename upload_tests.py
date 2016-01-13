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
Read JSOM files, each corresponding to a Ceph test, and upload to ElasticSearch.

Example:

python3 upload_tests.py --dir bootstrapping/ \\
  --elasticsearch elastic-ceph.bitergia.com:80 ceph-tests --esauth ceph XXX
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
    parser.add_argument("--dir", default = ".",
                        help = "Directory with test files")
    parser.add_argument("--elasticsearch", nargs=2,
                        help = "Url of elasticsearch, and index to use " + \
                        "(eg: http://localhost:9200 project)")
    parser.add_argument("--esauth", nargs=2, default = None,
                        help = "Authentication to access ElasticSearch" + \
                        "(eg: user password)")
    args = parser.parse_args()
    return args

def read_tests (dir):
    """
    Read test files from directory dir.

    :param dir: directory with test files

    :returns: a list with all the tests

    """

    files = [os.path.join(dir, file) for file in os.listdir(path = dir)]
    files = [file for file in files
                if os.path.isfile(file) and
                    os.path.splitext(file)[-1].lower() == ".json"]
    tests = {}
    for file in files:
        with open(file) as json_file:
            data = json.load(json_file)
            date = data["information"]["date"]
            uuid = data["information"]["cluster_uuid"]
            name = date + "_" + uuid
            tests[name] = data
    return tests

class Test(DocType):
    Id = String(index='not_analyzed')
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
    #cost_usable_tb = Float()
    Seq_Read_4M = Object(
        properties = {
            "MB/sec_per_OSD_Device": Integer(),
            "Cost_TB_per_MB/sec": Float(),
            "MB/sec_per_Cluster": Integer()
        }
    )
    fourMSR_mbsec_osd_device = Integer()
    fourMSR_cost_usable_tb_mbsec = Float()
    fourMSR_mbsec_cluster = Float()
    fourMSR_latency_avg = Float()
    #fourMSR_latency_95 = Float()
    fourMSW_mbsec_osd_device = Integer()
    fourMSW_cost_usable_tb_mbsec = Float()
    fourMSW_mbsec_cluster = Float()
    fourMSW_latency_avg = Float()
    #fourMSW_latency_95 = Float()

    class Meta:
        index = 'ceph-tests'

def upload_elasticsearch (tests, es_server, es_auth):
    """Upload to ElasticSearch.

    :param tests: dictionary with tests
    :param es_server: ElasticSearch data, list ["host:port", "index"]
    :param es_auth: ElasticSearch auth data, list ["user", "passwd"]

    """

    connections.create_connection(hosts=[es_server[0]],
                                http_auth=[es_auth[0], es_auth[1]])
    index = Index (es_server[1])
    index.delete(ignore = 404)
    Test.init()
    cont = 0
    for name, data in tests.items():
        cont = cont + 1
        for benchmark in data["benchmarks"]:
            if benchmark["suite"] == "CBT_Throughput-optimized":
                if benchmark["kind"] == "4M Sequential Read":
                    Seq_Read_4M = {}
                    Seq_Read_4M["MB/sec_per_OSD_Device"] = benchmark["mbsec_osd_device"]
                    Seq_Read_4M["Cost_TB_per_MB/sec"] = float(benchmark["mbsec_cluster"])
                    Seq_Read_4M["MB/sec_per_Cluster"] = benchmark["avg_latency"]
                    fourMSR_mbsec_osd_device = benchmark["mbsec_osd_device"]
                    fourMSR_mbsec_cluster = float(benchmark["mbsec_cluster"])
                    fourMSR_latency_avg = benchmark["avg_latency"]
                elif benchmark["kind"] == "4M Sequential Write":
                    fourMSW_mbsec_osd_device = benchmark["mbsec_osd_device"]
                    fourMSW_mbsec_cluster = float(benchmark["mbsec_cluster"])
                    fourMSW_latency_avg = benchmark["avg_latency"]
        config = str(data["platform"]["osds"]) + "/" \
            + data["platform"]["osd_media"] + "/" \
            + data["platform"]["ceph_data_protection"]
        test = Test (
                 meta={'id': name},
                 Id = name,
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
                 Seq_Read_4M = Seq_Read_4M,
                 fourMSR_mbsec_osd_device = fourMSR_mbsec_osd_device,
                 #fourMSR_cost_usable_tb_mbsec = data["4MSR_cost_usable_tb_mbsec"],
                 fourMSR_mbsec_cluster = fourMSR_mbsec_cluster,
                 fourMSR_latency_avg = fourMSR_latency_avg,
                 #fourMSR_latency_95 = data["4MSR_latency_95"],
                 fourMSW_mbsec_osd_device = fourMSW_mbsec_osd_device,
                 #fourMSW_cost_usable_tb_mbsec = data["4MSW_cost_usable_tb_mbsec"],
                 fourMSW_mbsec_cluster = fourMSW_mbsec_cluster,
                 fourMSW_latency_avg = fourMSW_latency_avg,
                 #fourMSW_latency_95 = data["4MSW_latency_95"]
                )
        #test.meta.id = name
        print(test)
        test.save()

if __name__ == "__main__":

    args = parse_args()
    tests = read_tests(args.dir)
    print(tests)
    print()
    upload_elasticsearch(tests, args.elasticsearch, args.esauth)
