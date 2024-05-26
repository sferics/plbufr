# (C) Copyright 2019- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from os import PathLike
import typing as T

#import polars as pl

from . import bufr_structure
from .high_level_bufr.bufr import BufrFile


def read_bufr(
    path_or_messages: str | bytes | PathLike[T.Any] | T.Iterable[T.MutableMapping[str, T.Any]],
    columns: T.Sequence[str] | str = [],
    filters: T.Mapping[str, T.Any] = {},
    filter_method: T.Callable = all,
    skip_na: bool = False,
    required_columns: bool | T.Iterable[str] = True,
    flat: bool = False,
    return_method: str = "df"
) -> T.Any #pl.DataFrame | pl.LazyFrame | T.Generator:
    """
    Read selected observations from a BUFR file into DataFrame.
    """

    if isinstance(path_or_messages, (str, bytes, PathLike)):
        with BufrFile(path_or_messages) as bufr_file:  # type: ignore
            return _read_bufr(
                bufr_file,
                columns=columns,
                filters=filters,
                filter_method=filter_method,
                skip_na=skip_na,
                required_columns=required_columns,
                flat=flat,
                return_method=return_method                
            )
    else:
        return _read_bufr(
            path_or_messages,
            columns=columns,
            filters=filters,
            filter_method=filter_method,
            skip_na=skip_na,
            required_columns=required_columns,
            flat=flat,
            return_method=return_method
        )


def _read_bufr(
    bufr_obj: T.Iterable[T.MutableMapping[str, T.Any]],
    columns: T.Sequence[str] | str = [],
    filters: T.Mapping[str, T.Any] = {},
    filter_method: T.Callable = all,
    skip_na: bool = False,
    required_columns: bool | T.Iterable[str] = True,
    flat: bool = False,
    return_method: str = "df"
) -> T.Any #pl.DataFrame | pl.LazyFrame | T.Generator
    if not flat:
        observations = bufr_structure.stream_bufr(
            bufr_file=bufr_obj,
            columns=columns,
            filters=filters,
            filter_method=filter_method,
            skip_na=skip_na,
            required_columns=required_columns
        )
        match return_method:
            case "df":
                from polars import DataFrame
                return DataFrame(observations, infer_schema_length=1000000)
            case "lf":
                from polars import LazyFrame
                return LazyFrame(observations, infer_schema_length=1000000)
            case "gt":
                return observations
    else:

        class ColumnInfo:
            def __init__(self) -> None:
                self.first_count = 0

        column_info = ColumnInfo()

        # returns a generator
        observations = bufr_structure.stream_bufr_flat(
            bufr_file=bufr_obj,
            columns=columns,
            filters=filters,
            filter_method=filter_method,
            skip_na=skip_na,
            required_columns=required_columns,
            column_info=column_info,
        )
        match return_method:
            case "df":
                from polars import DataFrame
                return DataFrame(observations, infer_schema_length=1000000)
            case "lf":
                from polars import LazyFrame
                return LazyFrame(observations, infer_schema_length=1000000)
            case "gt":
                return observations
        
        # compare the column count in the first record to that of the
        # dataframe. If the latter is larger, then there were non-aligned columns,
        # which were appended to the end of the dataframe columns.
        if column_info.first_count > 0 and column_info.first_count < len(df.columns):
            import warnings

            # temporarily overwrite warnings formatter
            original_formatwarning = warnings.formatwarning
            warnings.formatwarning = lambda msg, *args, **kwargs: f"Warning: {msg}\n"
            warnings.warn(
                f"not all BUFR messages/subsets have the same structure in the input file. Non-overlapping columns (starting with column[{column_info.first_count-1}] = {df.columns[column_info.first_count-1]}) were added to end of the resulting dataframe altering the original column order for these messages."
            )
            warnings.formatwarning = original_formatwarning

        return df
