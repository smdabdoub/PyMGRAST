#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download function annotated sequence data from MG-RAST in
FASTA format.
"""
# standard library imports
import argparse
# local imports
from mgr_api import api as mgapi

    
def write_annotated_fasta(data, outFN):
    """
    Takes output from the annotated sequence download (request_metagenome_annotation())
    and writes it out to a FASTA-formatted file:
    > metagenome_id|m5nr_id md5sum list_of_annotations
    sequence data
    """
    with open(outFN, 'w') as outF:
        outF.write('\n'.join(['>{} {} {}\n{}'.format(entry[0], entry[1], entry[3], entry[2]) for entry in data]))

        
def parse_metagenome_file(mgFN):
    """
    Read in and return a list of metagenome IDs in a file, one per line.
    """
    metagenomes = []
    with open(mgFN, 'rU') as inF:
        metagenomes.extend([line.strip() for line in inF.readlines()])
    return metagenomes


def handle_program_options():
    parser = argparse.ArgumentParser(description="Download function annotated \
                                     sequence data from MG-RAST in FASTA format")

    metagenome_type = parser.add_mutually_exclusive_group(required=True)
    metagenome_type.add_argument('-m','--metagenome_id',
                                 help="One or more metagenome IDs.")
    metagenome_type.add_argument('-f', '--metagenome_file', 
                                 help="Path to a file containing multiple \
                                       metagenome IDs")
    
    parser.add_argument('-a','--auth_key', default='',
                        help="MG-RAST web authentication key. Only required for projects \
                              and metagenomes marked private.")
    parser.add_argument('-d','--database', default='KEGG',
                        help="Name of a function database in m5nr, e.g. SEED, KEGG, KO.\
                              Default is KEGG.")
    parser.add_argument('-t','--type', default='function', 
                        choices=['organism', 'function', 'ontology', 'feature', 'md5'],
                        help="The annotation type to retrieve. One of the following: \
                        organism, function, ontology, feature, md5. Default is function.")
    parser.add_argument('-o', '--output_fp',
                        help="The path to the result file.")
    parser.add_argument('-v', '--verbose', action='store_true')

    return parser.parse_args()


def main():
    args = handle_program_options()
    if not args.output_fp:
        args.output_fp = args.metagenome_id + '.fna'

    metagenomes = []
    if args.metagenome_id is not None:
        metagenomes.append(args.metagenome_id)
    elif args.metagenome_file is not None:
        metagenomes.extend(parse_metagenome_file(args.metagenome_file))

    seq_data = []
    for mg_id in metagenomes:
        if args.verbose:
            print 'Downloading {} {} annotated sequence data for metagenome ID {}...'.format(args.database, args.type, mg_id)

        d = mgapi.sequence_annotation(mg_id, args.database, args.type, args.auth_key)
        seq_data.extend(d)
        
        if args.verbose:
            print '{} sequence records downloaded'.format(len(d))

    # write out final list of sequence data
    with open(args.output_fp, 'w') as outF:
        for entry in seq_data:
            outF.write('>{} {} {}\n{}\n'.format(entry[0], entry[1], entry[3], entry[2]))

    if args.verbose:
        print 'Sequence data written to: ' + args.output_fp


if __name__ == '__main__':
    main()
