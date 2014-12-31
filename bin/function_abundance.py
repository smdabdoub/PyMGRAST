#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download function abundance data for specified metagenomes
in BIOM format.
"""
# standard library imports
import argparse
# local imports
from mgr_api import api as mgapi


def parse_metagenome_file(mg_fp):
    """
    Read in and return a list of metagenome IDs in a file, one per line.
    """
    metagenomes = []
    with open(mg_fp, 'rU') as in_f:
        metagenomes.extend([line for line in in_f.read().splitlines() if line.strip() is not ''])
    return metagenomes


def handle_program_options():
    parser = argparse.ArgumentParser(description="Download function abundance\
                                                  data for metagenomes in BIOM\
                                                  format.")

    metagenome_type = parser.add_mutually_exclusive_group(required=True)
    metagenome_type.add_argument('-m','--metagenome_ids', nargs='*',
                                 help="One or more metagenome IDs.")
    metagenome_type.add_argument('-f', '--metagenome_file', 
                                 help="Path to a file containing multiple \
                                       metagenome IDs")
    
    parser.add_argument('-a','--auth_key', default='',
                        help="MG-RAST web authentication key. Only required for projects \
                              and metagenomes marked private.")
    parser.add_argument('-g','--group_lvl', default='function',
                        help="The lowest functional level to group results by.\
                              One of: level1, level2, level3, function.\
                              Default is 'function'.")
    parser.add_argument('-s','--source', default='Subsystems', 
                        choices=['Subsystems', 'NOG', 'COG', 'KO'],
                        help="The database to retrieve function data from: \
                        Subsystems, NOG, COG, KO. Default is Subsystems.")
    parser.add_argument('-o', '--output_fp', default='function_abundance.biom',
                        help="The path to the result file.")
    parser.add_argument('-v', '--verbose', action='store_true')

    return parser.parse_args()


def main():
    args = handle_program_options()

    metagenomes = []
    if args.metagenome_ids is not None:
        metagenomes.extend(args.metagenome_ids)
    elif args.metagenome_file is not None:
        metagenomes.extend(parse_metagenome_file(args.metagenome_file))

    if args.verbose:
        print 'Downloading data for the following metagenomes:'
        for mg in metagenomes:
            print mg

    func_data_req = mgapi.mgrast_request('matrix/function', 
                                         auth_key=args.auth_key, 
                                         params={'id': metagenomes, 
                                                 'group_level': args.group_lvl,
                                                 'source': args.source, 
                                                 'result_type': 'abundance'})

    if func_data_req.status_code != 200:
        print "Error encountered downloading data. Please retry."
        print "Message: {}".format(func_data_req.reason)
        return

    with open(args.output_fp, 'w') as out_f:
        out_f.write(func_data_req.text)
    
    if args.verbose:
        print 'Download complete. Data written to: ' + args.output_fp


if __name__ == '__main__':
    main()
