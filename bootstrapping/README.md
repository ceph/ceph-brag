# Bootstrapping Ceph-brag benchmarking JSON documents

Before there are enough JSON documents describing Ceph-brag benchmarks in the expected format (see [README.md in the rood directory](../README.md)), we are producing some. Those are based on benchmarks done in the past, with information collected in csv files ([ceph-tests-data-4kr.csv] and [ceph-tests-data-4ms.csv]).

The process for producing the JSON documents, in a format suitable for being consumed by the script producing the ElasticSearch index, is as follows (a working Python3 envirionment is assumed):

* Install Pandas:

```
pip3 insttall pandas
```

* Run the generator script:

```
python3 create-jsons.py
```

This will produce several JSON documents (files with .json extension) that can be used as input for the script generating the ElasticSearch index. To do that, go to the [README.md file in the main directory](../README.md) and follow instructions.

The file create-jsons.ipynb is a Jupyter Python notebook producing the same results than the script. In fact, the script is just the notebook, saved as Python code. In case changes are needed to the script, the process would be changing the notebook, and re-generating the script from there.


