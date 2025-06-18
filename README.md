# E-TSN

Implementation of the E-TSN scheduling algorithm. Please note the limitations below.

When using this code, please cite the original paper:

```
@InProceedings{Zhao2022,
  author    = {Zhao, Yi and Yang, Zheng and He, Xiaowu and Wu, Jiahang and Cao, Hao and Dong, Liang and Dang, Fan and Liu, Yunhao},
  booktitle = {2022 IEEE 42nd International Conference on Distributed Computing Systems (ICDCS)},
  title     = {E-TSN: Enabling Event-triggered Critical Traffic in Time-Sensitive Networking for Industrial Applications},
  doi       = {10.1109/ICDCS54860.2022.00072},
  pages     = {691-701},
  keywords  = {Industries;Schedules;Job shop scheduling;Jitter;Probabilistic logic;Fourth Industrial Revolution;Internet;Time-Sensitive Networking;Event-triggered critical traffic;Traffic Scheduling;Cyber physical system},
  year      = {2022},
}
```

and the paper this implementation contributes to:

**TODO add reference to our paper**

## Requirements

* Python (3.10 or later)
* docplex (2.25.236 or later)

## Usage

```
usage: main.py [-h] -n NETWORK -t TT_STREAMS -e ET_STREAMS [-v] [--raw-output]
               [-o OUTPUT] [--cplex CPLEX] [--threads THREADS]
               [--timelimit TIMELIMIT] [-N N]

options:
  -h, --help            show this help message and exit
  -n NETWORK, --network NETWORK
                        Path to the network graph file
  -t TT_STREAMS, --tt_streams TT_STREAMS
                        Path to the tt streams file
  -e ET_STREAMS, --et_streams ET_STREAMS
                        Path to the et streams file
  -v, --verbose         print a lot of debug outputs. Is overwritten by the
                        raw flag.
  --raw-output          If set, the output will be in a raw format. Overwrites
                        the verbose flag.
  -o OUTPUT, --output OUTPUT
                        Path to the output file
  --cplex CPLEX         Path to cplex executable
  --threads THREADS     Number of threads to be used at most
  --timelimit TIMELIMIT
                        solver time limit in seconds. Use negative values for
                        unlimited.
  -N N, --N N           Number of probabilistic streams
```
### Example

```
python main.py -n dummy_data/topology.json -t dummy_data/streams.json -e dummy_data/emergency_streams.json --verbose -o dummy_data/output_gcl.json

```

### Input Data

To get more input data, you can use the generation scripts in our adjacent repository ([here]()**TODO add link**).

Inputs files must adhere the format from the generation scripts. Example files are provided in the `dummy_data` folder.

## Limitations and Changes

We only implement the prudent reservation variant of the algorithm.

This implementation assumes that emergency traffic (ET) has always a higher priority than the time-triggered traffic (TT).
The original E-TSN paper assumed that there can be higher priority TT streams.

We added propagation delays and processing delays to the constraints when needed.

Considering the adjacent link constraint: we went with the textual description, not the formal one, since they differ and the textual one makes more sense.

