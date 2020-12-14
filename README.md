# A Python-based Simulator of Channel Access in IEEE 802.11 Networks using Simpy library

## Installation

- (Optional) Launch virtual env: `python3 -m venv env && source env/bin/activate`
- Install requirements : `pip install -r requirements.txt`

## Structure

Main program is located in `dcfsimpy` module.

`dcf-simpy-cli.py` is resposible for executin different simulation scenarios.

## Usage

This project is using `click` library to execute the program with pre defined simulation scenarios. For each of the possible scenarios there is a help function.

##### Listing simulation scenarios 

```bash
python3 dcf-simpy-cli.py  --help                                                              
Usage: dcf-simpy-cli.py [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose  Enable informational logging, use second time for debugging
                 logs.

  -h, --help     Show this message and exit.

Commands:
  run-changing-cw
  run-changing-mcs
  run-changing-payload
  run-changing-stations
  single-run
```

#### Executing simulation scenario

```bash
python3 dcf-simpy-cli.py  run-changing-stations --help
Usage: dcf-simpy-cli.py run-changing-stations [OPTIONS]

Options:
  -r, --runs INTEGER           Runs per stations number.
  --stations-start INTEGER     Starting number of stations.  [required]
  --stations-end INTEGER       Ending number of stations.  [required]
  -t, --simulation-time FLOAT  Duration of the simulation per stations number
                               in s.

  -p, --payload-size INTEGER   Size of payload in B.
  --cw-min INTEGER             Size of cw min.
  --cw-max INTEGER             Size of cw max.
  --r-limit INTEGER            Number of failed transmissions in a row.
  --seed INTEGER               Seed for simulation.
  -s, --skip-results           If provided, results are not saved.
  --skip-results-show          If provided, results are not shown, to show
                               results you can't skip-results.

  -m, --mcs-value INTEGER      Value of mcs.
  -h, --help                   Show this message and exit.
```

```bash
python3 dcf-simpy-cli.py  run-changing-stations -r 5 --stations-start=2 --stations-end=4 -t 1 
SEED = 0 N=2 CW_MIN = 15 CW_MAX = 1023  PCOLL: 0.1128 THR: 30.20544 FAILED_TRANSMISSIONS: 326 SUCCEEDED_TRANSMISSION 2565
SEED = 0 N=3 CW_MIN = 15 CW_MAX = 1023  PCOLL: 0.1751 THR: 30.123008 FAILED_TRANSMISSIONS: 543 SUCCEEDED_TRANSMISSION 2558
SEED = 0 N=4 CW_MIN = 15 CW_MAX = 1023  PCOLL: 0.2087 THR: 30.134784 FAILED_TRANSMISSIONS: 675 SUCCEEDED_TRANSMISSION 2559
```

#### Verbose mode

Just add -v or -vv after `python3 dcf-simpy-cli.py`