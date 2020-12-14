#!/usr/bin/env python3

import logging
import threading
from typing import Dict, List, Optional, Tuple

import click

import dcfsimpy


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Enable informational logging, use second time for debugging logs.",
)
def cli(verbose: int) -> None:
    if verbose > 1:
        logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    elif verbose > 0:
        logging.basicConfig(format="%(message)s", level=logging.INFO)
    else:
        logging.basicConfig(format="%(message)s", level=logging.WARNING)


@cli.command()
@click.option("-r", "--runs", "runs", default=10, help="Runs per stations number.")
@click.option(
    "--stations-start",
    "stations_start",
    type=int,
    required=True,
    help="Starting number of stations.",
)
@click.option(
    "--stations-end",
    "stations_end",
    required=True,
    type=int,
    help="Ending number of stations.",
)
@click.option(
    "-t",
    "--simulation-time",
    "simulation_time",
    default=100.0,
    help="Duration of the simulation per stations number in s.",
)
@click.option(
    "-p", "--payload-size", "payload_size", default=1472, help="Size of payload in B."
)
@click.option("--cw-min", "cw_min", default=15, help="Size of cw min.")
@click.option("--cw-max", "cw_max", default=1023, help="Size of cw max.")
@click.option(
    "--r-limit", "r_limit", default=7, help="Number of failed transmissions in a row.",
)
@click.option("--seed", default=1, help="Seed for simulation.")
@click.option(
    "-s",
    "--skip-results",
    "skip_results",
    is_flag=True,
    help="If provided, results are not saved.",
)
@click.option(
    "--skip-results-show",
    "skip_results_show",
    is_flag=True,
    help="If provided, results are not shown, to show results you can't skip-results.",
)
@click.option("-m", "--mcs-value", "mcs_value", default=7, help="Value of mcs.")
def run_changing_stations(
    runs: int,
    seed: int,
    stations_start: int,
    stations_end: int,
    simulation_time: int,
    skip_results: bool,
    cw_min: int,
    cw_max: int,
    r_limit: int,
    payload_size: int,
    mcs_value: int,
    skip_results_show: bool,
):
    config = dcfsimpy.Config(payload_size, cw_min, cw_max, r_limit, mcs_value)
    results = dict()
    backoffs = {
        key: {i: 0 for i in range(stations_start, stations_end + 1)}
        for key in range(cw_max + 1)
    }
    for _ in range(runs):
        threads = [
            threading.Thread(
                target=dcfsimpy.run_simulation,
                args=(
                    n,
                    seed * _,
                    simulation_time,
                    skip_results,
                    config,
                    backoffs,
                    results,
                ),
            )
            for n in range(stations_start, stations_end + 1)
        ]
        __start_threads(threads)
    if not skip_results:
        path = dcfsimpy.save_results(results, backoffs, "run_changing_stations")
        if not skip_results_show:
            dcfsimpy.show_results_changing_stations(path)


@cli.command()
@click.option("-r", "--runs", "runs", default=10, help="Runs per stations number.")
@click.option(
    "--stations-number",
    "stations_number",
    type=int,
    required=True,
    help="Number of stations.",
)
@click.option(
    "-t",
    "--simulation-time",
    "simulation_time",
    default=100.0,
    help="Duration of the simulation per stations number in s.",
)
@click.option(
    "-p", "--payload-size", "payload_size", default=1472, help="Size of payload in B."
)
@click.option("--cw-min", "cw_min", default=15, help="Size of cw min.")
@click.option("--cw-max", "cw_max", default=1023, help="Size of cw max.")
@click.option(
    "--r-limit", "r_limit", default=7, help="Number of failed transmissions in a row.",
)
@click.option("--seed", default=1, help="Seed for simulation.")
@click.option(
    "-s",
    "--skip-results",
    "skip_results",
    is_flag=True,
    help="If provided, results are not saved.",
)
def run_changing_mcs(
    runs: int,
    seed: int,
    stations_number: int,
    simulation_time: int,
    skip_results: bool,
    cw_min: int,
    cw_max: int,
    r_limit: int,
    payload_size: int,
):
    results = dict()
    backoffs = {key: {stations_number: 0} for key in range(cw_max + 1)}
    for _ in range(runs):
        threads = [
            threading.Thread(
                target=dcfsimpy.run_simulation,
                args=(
                    stations_number,
                    seed * _,
                    simulation_time,
                    skip_results,
                    dcfsimpy.Config(payload_size, cw_min, cw_max, r_limit, mcs_value),
                    backoffs,
                    results,
                ),
            )
            for mcs_value in range(0, 8)
        ]
        __start_threads(threads)
    if not skip_results:
        path = dcfsimpy.save_results(results, backoffs, "run_changing_mcs")
        dcfsimpy.show_results_changing_mcs(path)


@cli.command()
@click.option("-r", "--runs", "runs", default=10, help="Runs per stations number.")
@click.option(
    "--stations-start",
    "stations_start",
    type=int,
    required=True,
    help="Starting number of stations.",
)
@click.option(
    "--stations-end",
    "stations_end",
    required=True,
    type=int,
    help="Ending number of stations.",
)
@click.option(
    "--stations-step",
    "stations_step",
    default=5,
    type=int,
    help="Step number of stations.",
)
@click.option(
    "-t",
    "--simulation-time",
    "simulation_time",
    default=100.0,
    help="Duration of the simulation per stations number in s.",
)
@click.option(
    "-p", "--payload-size", "payload_size", default=1472, help="Size of payload in B."
)
@click.option("--cw-min-start", "cw_min_stop", default=3, help="Size of cw min start.")
@click.option("--cw-min-stop", "cw_min_stop", default=1023, help="Size of cw min stop.")
@click.option("--cw-max", "cw_max", default=1023, help="Size of cw max.")
@click.option(
    "--r-limit", "r_limit", default=7, help="Number of failed transmissions in a row.",
)
@click.option("--seed", default=1, help="Seed for simulation.")
@click.option(
    "-s",
    "--skip-results",
    "skip_results",
    is_flag=True,
    help="If provided, results are not saved.",
)
@click.option("-m", "--mcs-value", "mcs_value", default=7, help="Value of mcs.")
# @click.option("-p", "--results-path", "results_path", help="Path to save results, default results/timestamp.")
# @click.option("--results-prefix", "results_prefix", default=None, help="Prefix for results files.")
def run_changing_cw(
    runs: int,
    seed: int,
    stations_start: int,
    stations_end: int,
    stations_step: int,
    simulation_time: int,
    skip_results: bool,
    cw_min_start: int,
    cw_min_stop: int,
    cw_max: int,
    r_limit: int,
    payload_size: int,
    mcs_value: int,
):
    # config = dcfsimpy.Config(payload_size, cw_min, cw_max, r_limit)
    results = dict()
    backoffs = {
        key: {i: 0 for i in range(stations_start, stations_end + 1)}
        for key in range(cw_max + 1)
    }
    for cw_min in [
        pow(2, x) - 1
        for x in range(int((cw_min_start + 1) / 2), int((cw_min_stop + 1) / 2))
    ]:
        for _ in range(runs):
            threads = [
                threading.Thread(
                    target=dcfsimpy.run_simulation,
                    args=(
                        n,
                        seed * _,
                        simulation_time,
                        skip_results,
                        dcfsimpy.Config(
                            payload_size, cw_min, cw_max, r_limit, mcs_value
                        ),
                        backoffs,
                        results,
                    ),
                )
                for n in range(stations_start, stations_end + 1, stations_step)
            ]
            __start_threads(threads)
    if not skip_results:
        path = dcfsimpy.save_results(results, backoffs, "run_changing_cw")
        dcfsimpy.show_results_changing_cw(path)


@cli.command()
@click.option("-r", "--runs", "runs", default=10, help="Runs per stations number.")
@click.option(
    "--stations-number",
    "stations_number",
    type=int,
    required=True,
    help="Number of stations.",
)
@click.option(
    "-t",
    "--simulation-time",
    "simulation_time",
    default=100.0,
    help="Duration of the simulation per stations number in s.",
)
@click.option(
    "--payload-start-size",
    "payload_start_size",
    default=100,
    help="Size of starting payload in B.",
)
@click.option(
    "--payload-end-size",
    "payload_end_size",
    default=2000,
    help="Size of ending payload in B.",
)
@click.option(
    "--payload-step-size", "payload_step_size", default=100, help="Size of step in B."
)
@click.option("--cw-min", "cw_min", default=15, help="Size of cw min.")
@click.option("--cw-max", "cw_max", default=1023, help="Size of cw max.")
@click.option(
    "--r-limit", "r_limit", default=7, help="Number of failed transmissions in a row.",
)
@click.option("--seed", default=1, help="Seed for simulation.")
@click.option(
    "-s",
    "--skip-results",
    "skip_results",
    is_flag=True,
    help="If provided, results are not saved.",
)
@click.option("-m", "--mcs-value", "mcs_value", default=7, help="Value of mcs.")
def run_changing_payload(
    runs: int,
    seed: int,
    stations_number: int,
    simulation_time: int,
    skip_results: bool,
    cw_min: int,
    cw_max: int,
    r_limit: int,
    payload_start_size: int,
    payload_end_size: int,
    payload_step_size: int,
    mcs_value: int,
):
    results = dict()
    backoffs = {key: {stations_number: 0} for key in range(cw_max + 1)}
    for _ in range(runs):
        threads = [
            threading.Thread(
                target=dcfsimpy.run_simulation,
                args=(
                    stations_number,
                    seed * _,
                    simulation_time,
                    skip_results,
                    dcfsimpy.Config(payload_size, cw_min, cw_max, r_limit, mcs_value),
                    backoffs,
                    results,
                ),
            )
            for payload_size in range(
                payload_start_size, payload_end_size + 1, payload_step_size
            )
        ]
        __start_threads(threads)
    if not skip_results:
        path = dcfsimpy.save_results(results, backoffs, "run_changing_payload")
        dcfsimpy.show_results_changing_payload(path)


@cli.command()
@click.option(
    "--stations-number",
    "stations_number",
    type=int,
    required=True,
    help="Number of stations.",
)
@click.option(
    "-t",
    "--simulation-time",
    "simulation_time",
    default=100.0,
    help="Duration of the simulation per stations number in s.",
)
@click.option(
    "--payload-size", "payload_size", default=1472, help="Size of  payload in B."
)
@click.option("-m", "--mcs-value", "mcs_value", default=7, help="Value of mcs.")
@click.option("--cw-min", "cw_min", default=15, help="Size of cw min.")
@click.option("--cw-max", "cw_max", default=1023, help="Size of cw max.")
@click.option(
    "--r-limit", "r_limit", default=7, help="Number of failed transmissions in a row.",
)
@click.option("--seed", default=1, help="Seed for simulation.")
@click.option(
    "-s",
    "--skip-results",
    "skip_results",
    is_flag=True,
    help="If provided, results are not saved.",
)
def single_run(
    seed: int,
    stations_number: int,
    simulation_time: int,
    skip_results: bool,
    cw_min: int,
    cw_max: int,
    r_limit: int,
    payload_size: int,
    mcs_value: int,
):
    results = dict()
    backoffs = {key: {stations_number: 0} for key in range(cw_max + 1)}
    dcfsimpy.run_simulation(
        stations_number,
        seed,
        simulation_time,
        skip_results,
        dcfsimpy.Config(payload_size, cw_min, cw_max, r_limit, mcs_value),
        backoffs,
        results,
    )

    if not skip_results:
        dcfsimpy.save_results(results, backoffs, "single_run")


def __start_threads(threads: List[threading.Thread]):
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    cli(obj=None)
