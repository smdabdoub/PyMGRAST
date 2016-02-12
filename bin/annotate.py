#!/usr/bin/env python
'''
Annotate a file containing unique identifiers from an index file 
with matching gene/transcript/... IDs.

Author: Shareef M Dabdoub
'''
import argparse
import csv
import os.path as osp

def handle_program_options():
    parser = argparse.ArgumentParser(description="Annotate a file containing\
                                     unique identifiers from an index file with\
                                     matching gene/transcript/... IDs.")
    parser.add_argument('-i', '--index_fp', required=True,
                        help="Path to the file containing the ID-based\
                        annotations. NOTE: This file must contain the unique ID\
                        for each entry as the first column.")
    parser.add_argument('-a', '--annotate_fp', required=True,
                        help="Path to the file to be annotated.")
    parser.add_argument('-o', '--output_fp',
                        help="Path to the (tab-separated) annotated results\
                        file. By default, the output file will be written to\
                        the same directory as the input file with '_ann'\
                        appended to the file name.")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Prints status messages during program execution.")

    return parser.parse_args()


def main():
    args = handle_program_options()

    # parse index file
    with open(args.index_fp, 'rU') as inf:
        index_DR = csv.DictReader(inf, delimiter='\t')
        id_column = index_DR.fieldnames[0]
        index = {line[id_column]: line for line in index_DR}

    # create output file path
    if not args.output_fp:
        deseq_fp_split = osp.splitext(args.deseq_results_fp)
        out_fp = deseq_fp_split[0] + "_ann.txt"


    # parse the file to be annotated
    with open(args.deseq_results_fp, 'rU') as deseq_f:
        ann_DR = csv.DictReader(deseq_f, delimiter=',')
        ann_id_column = ann_DR.fieldnames[0]
        ann_res = [line for line in ann_DR]

    # update the results data with annotations
    for entry in ann_res:
        ann_id = entry[ann_id_column]
        if ann_id in index:
            entry.update(index[ann_id])
        else:
            print "ID '{}'' not found, skipping.".format(ann_id)
            blank_annotation = {field: '' for field in index_DR.fieldnames[0]}
            blank_annotation[id_column] = ann_id
            entry.update(blank_annotation)

    # output the annotated results
    out_header = index_DR.fieldnames + ann_DR.fieldnames[1:]
    out_line = "\t".join(['{'+item+'}' for item in out_header]) + '\n'

    with open(out_fp, 'w') as outf:
        outf.write('\t'.join(out_header) + '\n')
        for entry in ann_res:
            outf.write(out_line.format(**entry))

    print "Annotated results written to: {}".format(out_fp)


if __name__ == '__main__':
    main()