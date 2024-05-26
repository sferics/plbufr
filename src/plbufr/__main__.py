# (C) Copyright 2019- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from argparse import ArgumentParser
import typing as T

from eccodes import codes_get_api_version  # type: ignore


def main(argv: T.Optional[list[str]] = None) -> None:
    parser = ArgumentParser()
    parser.add_argument("command")
    args = parser.parse_args(args=argv)
    if args.command == "selfcheck":
        print("Found: ecCodes v%s." % codes_get_api_version())
        print("Your system is ready.")
    else:
        raise RuntimeError(
            "Command not recognised %r. See usage with --help." % args.command
        )


if __name__ == "__main__":
    main()  # pragma: no cover
