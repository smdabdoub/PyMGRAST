#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extract the set of sequences that were filtered 
out after the MG-RAST screening against the human
genome step.
"""
from __future__ import absolute_import, division, print_function

# standard library imports
import argparse
from io import StringIO
import os, os.path as osp
import sys
import time, datetime
# local imports
from mgr_api import api as mgapi


def create_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def duration(start, end):
    return str(datetime.timedelta(seconds=int(end - start)))


def parse_metagenome_file(mg_fp):
    """
    Read in and return a list of metagenome IDs in a file, one per line.
    """
    metagenomes = []
    with open(mg_fp, 'rU') as in_f:
        metagenomes.extend([line.strip() for line in in_f.readlines()])
    return metagenomes


def stage_info(stage_id, mg_id, auth_key):
    stage = mgapi.mgrast_request('download', mg_id, {'stage': stage_id}, auth_key=auth_key)
    if stage.status_code == 200:
        return stage.json()
    else:
        stage.raise_for_status()


def handle_program_options():
    parser = argparse.ArgumentParser(description="Download metagenome data for\
                                     a specified stage of the MG-RAST\
                                     pipeline.")

    metagenome_type = parser.add_mutually_exclusive_group(required=True)
    metagenome_type.add_argument('-m', '--metagenome_id',
                                 help="One or more metagenome IDs.")
    metagenome_type.add_argument('-f', '--metagenome_file',
                                 help="Path to a file containing multiple \
                                       metagenome IDs")

    parser.add_argument('-a', '--auth_key', default='',
                        help="MG-RAST web authentication key. Only required for\
                              metagenomes marked private.")
    parser.add_argument('-s', '--stage_id', default='',
                        help="Numeric identifier for the stage in the MG-RAST\
                        pipeline to download.")
    parser.add_argument('--substage',
                        help="Substage identifier. Some stages have multiple\
                        files associated with them. The dereplication stage,\
                        for example, has substages 'passed' and 'removed'. If\
                        this option is not specified, the first returned\
                        file entry will be downloaded.")
    parser.add_argument('-o', '--out_dir', default='.',
                        help="The path to the output directory (default is\
                              the current directory). One FASTA-format file\
                              will be created for each specified metagenome\
                              and saved in this directory.")
    parser.add_argument('-v', '--verbose', action='store_true')

    return parser.parse_args()


def main():
    args = handle_program_options()

    if osp.isfile(args.out_dir):
        print("--out_dir (-o) option must be a valid directory and not a file",
              file=sys.stderr)
        sys.exit(1)

    # will fail gracefully if dir exists
    try:
        create_dir(args.out_dir)
    except OSError as ose:
        print("Error creating dir ({}): {}".format(args.out_dir))
        sys.exit(1)

    metagenomes = []
    if args.metagenome_id is not None:
        metagenomes.append(args.metagenome_id)
    elif args.metagenome_file is not None:
        metagenomes.extend(parse_metagenome_file(args.metagenome_file))
        
    if args.verbose:
        if args.metagenome_file is not None:
            msg = "Downloading stage {} data for {} metagenome(s) found in: {}"
            print(msg.format(args.stage_id, len(metagenomes), 
                  args.metagenome_file))
        else:
            msg = "Downloading stage {} for metagenome {}"
            print(msg.format(args.stage_id, args.metagenome_id))

    # MG-RAST stage.file ids for downloading
    #derep_passed = '150'
    #screen_passed = '299'

    for mg_id in metagenomes:
        sinfo = stage_info(args.stage_id, mg_id, args.auth_key)
        sdata = sinfo['data']
        types = []

        if args.substage:
            for substage in sdata:
                ss_name = substage['stage_name'].split('.')[-1]
                types.append(ss_name)
                if ss_name == args.substage:
                    sdata = substage
                    break
            else:
                print("Substage '{}' not found".format(args.substage))
                print("Available substages {}:".format(args.stage_id))
                for ss in types:
                    print("  {}".format(ss))
                sys.exit(1)
        
        file_id = sdata['file_id']
        file_name = sdata['file_name']

        if args.verbose:
            print('\tDownloading file: {}...'.format(file_name), end='')
            sys.stdout.flush()

        start = time.time()
        stage = mgapi.mgrast_request('download', mg_id,
                                     {'file': file_id},
                                     auth_key=args.auth_key)
        end = time.time()

        if args.verbose:
            print("completed in: {}".format(duration(start, end)))
        
        out_fp = osp.join(args.out_dir, file_name)
        with open(out_fp, 'w') as outf:
            outf.write(StringIO(stage.text).getvalue())

        if args.verbose:
            print('\tData written to: ' + out_fp)


if __name__ == '__main__':
    main()
