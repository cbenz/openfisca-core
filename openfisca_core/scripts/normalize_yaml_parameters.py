#! /usr/bin/env python


"""Normalize a YAML parameter tree, loading it from a directory and re-writing it to another one.

This allows in particular to ensure that each YAML file contains exactly one parameter.
"""


import argparse
from pathlib import Path
import sys

from openfisca_core.parameters import load_parameter_file, Parameter, ParameterNode, save_parameters_to_dir


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    parser.add_argument('source_dir', type = Path, help = "directory with parameters to read")
    parser.add_argument('target_dir', type = Path, help = "directory where parameters are written")
    args = parser.parse_args()

    if not args.source_dir.is_dir():
        parser.error("Invalid source_dir")
    if not args.target_dir.is_dir():
        args.target_dir.mkdir()

    parameters = load_parameter_file(args.source_dir)
    save_parameters_to_dir(parameters, args.target_dir)


if __name__ == "__main__":
    sys.exit(main())
