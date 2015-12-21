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
A properly formatted submission should come in the format of a pull request with a named folder in the format of "[Date][Time][cluster_uuid]" which will contain the following:
* JSON file following the format of example.json
* A hardware info dump
* A copy of sysctl
* A copy of your crushmap
* A pruned version of CBT results set

For instructions on how to generate these files, read below:
