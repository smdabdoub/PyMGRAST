#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Take multiple transposed abundance tables (see abundance_table_transpose.py)
and merge them on the list of functions (level 1...level4), e.g. KEGG or mg_func
data.
"""
import argparse
from collections import defaultdict, Counter
import csv


def add_data(mg_func, table, key_cols):
    for entry in table:
        key = "@@".join(["{}" for _ in range(len(key_cols))]).format(*[entry[label] for label in key_cols])
        for ekey in entry:
            if ekey not in key_cols:
                mg_func[key][ekey] = entry[ekey]


def write_table(mg_func, mgids, key_cols, out_fp):
    with open(out_fp, 'w') as out_f:
        out_f.write('\t'.join(key_cols) + '\t')
        out_f.write('\t'.join(mgids) + '\n')
        for func in sorted(mg_func.keys()):
            out_f.write('\t'.join(func.split('@@')) + '\t')
            out_f.write('\t'.join([mg_func[func][mgid] if mgid in mg_func[func] else '0' for mgid in mgids]) + '\n')


def parse_key_columns(fp, stop_col):
    """
    Given an input file and a (1-indexed) column number,
    grab all column headers including and preceding 
    stop_col for use as a unique key in identifying
    rows.
    """
    with open(fp, 'rU') as fh:
        csvr = csv.reader(fh, delimiter="\t")
        header = csvr.next()
        return header[:stop_col]


def handle_program_options():
    """
    Parses the given options passed in at the command line.
    """
    parser = argparse.ArgumentParser(description="Take multiple transposed\
                                     abundance tables and merge them on the\
                                     list of functions (level 1...level 4),\
                                     e.g. KEGG or mg_func data.")
    parser.add_argument('abd_table_fps', nargs="+",
                        help="Paths to two or more transposed abundance tables.")
    parser.add_argument('--stop_column', default=1, type=int,
                        help="The index of the last column before the abundance\
                              data begins. All columns up to and including this\
                              one will be combined into a unique key used to\
                              identify rows for the merge operation.")
    parser.add_argument('-o', '--output_fp', default="merged_table.txt",
                        help="The output file path.")

    return parser.parse_args()


def main():
    args = handle_program_options()

    mg_func_abd = defaultdict(lambda : defaultdict(str))
    mg_ids = []

    key_cols = parse_key_columns(args.abd_table_fps[0], args.stop_column)

    for fp in args.abd_table_fps:
        with open(fp, 'rU') as fh:
            abd_table = [line for line in csv.DictReader(fh, delimiter='\t')]
            add_data(mg_func_abd, abd_table, key_cols)
            mg_ids.extend(sorted([col_id for col_id in abd_table[0] if col_id not in key_cols]))

    write_table(mg_func_abd, mg_ids, key_cols, args.output_fp)


if __name__ == "__main__":
    main()