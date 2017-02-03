# ceph-brag
Ceph performance testing results repository.

# Submission Requirements
In order to have your Ceph performance results included in this repository you need to meet a few simple requirements:
* Tests must be run with the CBT test harness (to ensure comparability)
* Test setups must include >= 3 OSD servers
* Test setups must include >= 2 OSD devices per server
* IOPS/latency must be measured from the client perspective
* Submitter must be willing to make results public
 
# What to submit
A properly formatted submission should come in the format of a pull request with a named folder in the format of:
* "[Date]\_[Time(HHMMSS)]\_[cluster_uuid]" 
 
Which should contain the following:
* JSON file following the format of example.json
* A hardware info dump
* A copy of sysctl
* A copy of your crushmap
* A pruned version of CBT results set

For instructions on how to generate these files, read below:

[To be done]

# How to generate an ElasticSearch index from submissions

We can use performance testing submissions to produce an ElasticSearch index, which can be shown with Kibana dashboards (see below).

To produce that index, run the [upload_tests.py script](upload_tests.py), as follows (a working Python3 environment is assumed):

* Install ElasticSearch-dsl:

```
pip3 install elasticsearch_dsl
```

* Run the script to generate the index. In this example, we will use the bootstrapping JSON documents to produce the index, assuming the ElasticSearch instance is at `http://elastic-ceph.bitergia.com:80`, with auth credentials ceph / XXX, and that the index to be created is `ceph-tests`. For more information about the bootstrapping JSON documents, read the [corresponding READM.md file](bootstrapping/README.md)

```
python3 upload_tests.py --dir bootstrapping/ \
  --elasticsearch https://elasticsearch.bitergia.com/ceph ceph-tests --esauth ceph XXX
```

You can use any name for the index, but if you intend to use the Kibana dashboard provided in this directory, the index should be named `ceph-tests`.

# How to produce a Kibana dashboard to visualize submissions

Once the ElasticSearch index is created, we can produce a Kibana4 dashboard for visualizing its contents. For that, deploy a Kibana instance which uses the ElasticSearch instance where the index was uploaded (see above). Then, upload the [dashboard description kibana-export.json](kibana-export.json). For that, in Kibana4, click on "Settings", "Objects", "Import", and when prompted, select the mentioned file. Three dashboards, and all the needed visualizations, will be imported into Kibana: `Simple`, `Simple Random`, `Simple Sequential`.
