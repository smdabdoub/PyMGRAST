#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extract the set of sequences that were filtered 
out after the MG-RAST screening against the human
genome step.
"""
from __future__ import print_function

# standard library imports
import argparse
from io import StringIO
import os.path as osp
import sys
# 3rd party imports
from skbio import util as skbu, SequenceCollection
# local imports
from mgr_api import api as mgapi


def extract_seq_ids(data, fmt='fasta', variant=None):
    """
    Given FASTQ-format data (string), parse out only the
    sequence IDs and return.
    """
    fh = StringIO(data)
    if fmt == 'fastq':
        sc = SequenceCollection.read(fh, format=fmt, variant=variant)
    else:
        sc = SequenceCollection.read(fh, format=fmt)
    return frozenset(entry.id for entry in sc)


def filter_seqs(seqs, remove_ids):
    """
    Given a collections of sequences and a set of IDs to remove,
    return all sequences that do not match those IDs.

    :type seqs: skbio.SequenceCollection
    :param seqs: The sequences to be filtered
    :type remove_ids: set
    :param remove_ids: A set of sequence IDs to remove from the sequence data
    :rtype: SequenceCollection
    """
    return SequenceCollection([seq for seq in seqs if seq.id not in remove_ids])


def parse_metagenome_file(mg_fp):
    """
    Read in and return a list of metagenome IDs in a file, one per line.
    """
    metagenomes = []
    with open(mg_fp, 'rU') as in_f:
        metagenomes.extend([line.strip() for line in in_f.readlines()])
    return metagenomes


def handle_program_options():
    parser = argparse.ArgumentParser(description="Extract the set of sequences\
                                     that were filtered out after the MG-RAST\
                                     screening against the human genome step.\
                                     This is done by removing the sequences\
                                     that did not match the human genome from\
                                     the set of sequences that passed\
                                     dereplication (the prior step).")

    metagenome_type = parser.add_mutually_exclusive_group(required=True)
    metagenome_type.add_argument('-m', '--metagenome_id',
                                 help="One or more metagenome IDs.")
    metagenome_type.add_argument('-f', '--metagenome_file',
                                 help="Path to a file containing multiple \
                                       metagenome IDs")

    parser.add_argument('-a', '--auth_key', default='',
                        help="MG-RAST web authentication key. Only required for\
                              metagenomes marked private.")
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
    skbu.create_dir(args.out_dir)

    metagenomes = []
    if args.metagenome_id is not None:
        metagenomes.append(args.metagenome_id)
    elif args.metagenome_file is not None:
        metagenomes.extend(parse_metagenome_file(args.metagenome_file))
        
    if args.verbose:
        msg = 'Processing requested for {} metagenome(s) found in: {}'
        print(msg.format(len(metagenomes), args.metagenome_file))

    # MG-RAST stage.file ids for downloading
    derep_passed = '150.1'
    screen_passed = '299.1'

    for mg_id in metagenomes:
        if args.verbose:
            print('Processing metagenome: {}'.format(mg_id))
            print('\tDownloading: Dereplication Passed...', end='')
            sys.stdout.flush()
        derepp_rsp = mgapi.mgrast_request('download', mg_id,
                                          {'file': derep_passed},
                                          auth_key=args.auth_key)
        derepp_sc = SequenceCollection.read(StringIO(derepp_rsp.text),
                                            format='fastq',
                                            variant='illumina1.8')
        if args.verbose:
            print('{} sequences'.format(len(derepp_sc)))
            print('\tDownloading: Screen Passed...', end='')
            sys.stdout.flush()
        screenp_rsp = mgapi.mgrast_request('download', mg_id,
                                           {'file': screen_passed},
                                           auth_key=args.auth_key)
        screenp_ids = extract_seq_ids(screenp_rsp.text, fmt='fastq',
                                      variant='illumina1.8')
        if args.verbose:
            print('{} sequences'.format(len(screenp_ids)))

        # filter dereplication passed with IDs from screen passed
        failed_screen = filter_seqs(derepp_sc, screenp_ids)
        if args.verbose:
            nsp = len(screenp_ids)
            print('\tRemoved {} sequences from Dereplication Passed'.format(nsp))
            print('\tleaving {} sequences'.format(len(failed_screen)))

        out_fp = osp.join(args.out_dir, mg_id + '_screen_failed.fastq')
        failed_screen.write(out_fp, format='fastq', variant='illumina1.8')
        if args.verbose:
            print('Sequence data written to: ' + out_fp)


if __name__ == '__main__':
    main()
