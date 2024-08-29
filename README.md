# E-TSN

Implementation of the E-TSN scheduling algorithm.

Y. Zhao et al., "E-TSN: Enabling Event-triggered Critical Traffic in Time-Sensitive Networking for Industrial Applications," 2022 IEEE 42nd International Conference on Distributed Computing Systems (ICDCS), Bologna, Italy, 2022, pp. 691-701, doi: 10.1109/ICDCS54860.2022.00072.



## Requirements

* Python (3.10 or later)
* docplex (2.25.236 or later)
* 

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

## Limitations and Changes

This implementation assumes that emergency traffic (ET) has always a higher priority than the time-triggered traffic (TT).
The original E-TSN paper assumed that there can be higher priority TT streams.

We added propagation delays and processing delays to the constraints when needed.

Considering the adjacent link constraint: we went with the textual description, not the formal one, since they differ and the textual one makes more sense.

