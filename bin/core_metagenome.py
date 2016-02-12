#!/usr/bin/env python
'''
Given an abundance file, extract the core metagenome;
where core is defined as those genes present in a some
percent of all samples (80 percent by default).

Author: Shareef M Dabdoub
'''
import argparse
import csv
import os.path as osp

def handle_program_options():
    parser = argparse.ArgumentParser(description="Given an abundance file,\
                                     extract the core metagenome; where core\
                                     is defined as those genes present in a\
                                     some percent of all samples (80 percent\
                                     by default)")
    parser.add_argument('-i', '--input_fp', required=True,
                        help="Path and name of the gene abundance file.")

    cutoff_args = parser.add_mutually_exclusive_group()
    cutoff_args.add_argument('-p', '--min_core_percent', 
                             default=0.8, type=float,
                             help="The minimum percent (rounded down) of samples\
                             a gene must be present in to be considered part of\
                             the core metagenome.")
    cutoff_args.add_argument('-n', '--min_core_samples', type=int,
                             help="The minimum number of samples (as a whole\
                             number) a gene must be present in to be considered\
                             part of the core metagenome.")

    parser.add_argument('-s', '--sample_start_column', required=True, type=int,
                        help="The column number of the first sample abundance\
                        data. This also assumes that the column containing\
                        unique IDs (e.g. KO IDs, EC Numbers, etc...) is\
                        immediately before the sample start column.")
    parser.add_argument('-o', '--output_fp',
                        help="Path and name of the output core metagenome\
                        file. The written data will be in the same format as\
                        the input file, but retaining only those rows matching\
                        genes determined to be in the core.")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Prints status messages while the program is\
                              running.")

    return parser.parse_args()


def main():
    args = handle_program_options()

    # parse metagenome abundance file
    with open(args.input_fp, 'rU') as in_f:
        dr = csv.DictReader(in_f, delimiter="\t")
        id_col = dr.fieldnames[args.sample_start_column-2]
        sample_ids = dr.fieldnames[args.sample_start_column-1:]
        abundance = [line for line in dr]

    row_counts = {row[id_col]: sum([1 if row[sid] is not "0" else 0 
                                    for sid in sample_ids]) 
                  for row in abundance}

    # detetermine core membership
    if args.min_core_samples is not None:
        min_core_amt = args.min_core_samples
    else:
        min_core_amt = int(len(sample_ids) * args.min_core_percent)

    core = {gene_id for gene_id in row_counts 
            if row_counts[gene_id] >= min_core_amt}

    # write core metagenome file
    with open(args.output_fp, 'w') as out_f:
        dwriter = csv.DictWriter(out_f, dr.fieldnames, delimiter="\t")
        dwriter.writeheader()
        dwriter.writerows([row for row in abundance if row[id_col] in core])

    if args.verbose:
        print "Input samples: {}".format(len(sample_ids))
        print "Input genes: {}".format(len(abundance))
        print "Samples in core: {}".format(min_core_amt)
        print "Genes in core: {}".format(len(core))
        print "\nCore file written to: {}".format(args.output_fp)



if __name__ == '__main__':
    main()