#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from collections import defaultdict

def handle_program_options():
    parser = argparse.ArgumentParser(description="Turn a list of subsystem \
                                                  abundance into a table with the first\
                                                  column representing subsystems, \
                                                  subsequent columns being metagenome \
                                                  IDs, and table data representing \
                                                  abundance for each subsystem and \
                                                  metagenome ID.")
    parser.add_argument('-i', '--input_list_fp', required=True,
                        help="The metagenome subsystem abundance list.")
    parser.add_argument('-o', '--output_fp', required=True,
                        help="The output file name.")
    parser.add_argument('-s', '--subsystem_level', default=3, choices=[1,2,3], type=int,
                        help="The maximum metagenomic subsystem level in which to bin \
                              the abundance results. Default is 3 (all levels).")

#    parser.add_argument('-v', '--verbose', action='store_true')

    return parser.parse_args()


def main():
    args = handle_program_options()
    mg_abundance = defaultdict(lambda: defaultdict(int))
    subsystems = set()

    with open(args.input_list_fp, 'rU') as inF:
        mg_subsys = [line.strip().split('\t') for line in inF][1:]
    
    for row in mg_subsys:
        max_lvl = 4-(3-args.subsystem_level)
        subsys = '@'.join([entry.strip('"') for entry in row[1:max_lvl]])
        mg_abundance[row[0]][subsys] += int(row[-1])
        subsystems.add(subsys)

    with open(args.output_fp, 'w') as outF:
        outF.write(''.join(['\t' for _ in range(args.subsystem_level)])+'\t'.join(mg_abundance.keys())+'\n')
        out_line = '\t'.join([l for l in ['{lvl1}','{lvl2}','{lvl3}'][:args.subsystem_level]])+'\t{abd}\n'
        for subsys in subsystems:
            abd = []
            for mgid in mg_abundance:
                abd.append(0 if subsys not in mg_abundance[mgid] else mg_abundance[mgid][subsys])
            subsys_lvls = subsys.split('@')
            out_args = {k:l for k,l in zip(['lvl1','lvl2','lvl3'][:args.subsystem_level], subsys_lvls)}
            out_args['abd'] = '\t'.join(map(str,abd))
            outF.write(out_line.format(**out_args))


if __name__ == '__main__':
    main()