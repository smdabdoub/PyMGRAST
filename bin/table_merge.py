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


def add_data(mg_func, condition):
    for entry in condition:
        key = "{};;{};;{};;{}".format(entry['level 1'], entry['level 2'], 
                                      entry['level 3'], entry['level 4'])
        for ekey in entry:
            if 'level' not in ekey:
                mg_func[key]['mgm'+ekey] = entry[ekey]


def write_table(mg_func, mgids, out_fp):
    with open(out_fp, 'w') as out_f:
        out_f.write('Level 1\tLevel 2\tLevel 3\tLevel 4\t')
        out_f.write('\t'.join(mgids) + '\n')
        for func in sorted(mg_func.keys()):
            out_f.write('\t'.join(func.split(';;')) + '\t')
            out_f.write('\t'.join([mg_func[func][mgid] if mgid in mg_func[func] else '0' for mgid in mgids]) + '\n')


def handle_program_options():
    """
    Parses the given options passed in at the command line.
    """
    parser = argparse.ArgumentParser(description="Take multiple transposed\
                                     abundance tables and merge them on the\
                                     list of functions (level 1...level 4),\
                                     e.g. KEGG or mg_func data.")
    parser.add_argument('abd_tables_fp', nargs="+",
                        help="Paths to two or more transposed abundance tables.")
    parser.add_argument('-o', '--output_fp', default="merged_table.txt",
                        help="The output file path.")

    return parser.parse_args()


def main():
    args = handle_program_options()

    mg_func_abd = defaultdict(lambda : defaultdict(str))
    mg_ids = []

    for fp in args.abd_tables_fp:
        with open(fp, 'rU') as fh:
            abd_table = [line for line in csv.DictReader(fh, delimiter='\t')]
            add_data(mg_func_abd, abd_table)
            mg_ids.extend(sorted(["mgm"+entry for entry in abd_table[0] if 'level' not in entry]))

    write_table(mg_func_abd, mg_ids, args.output_fp)


if __name__ == "__main__":
    main()