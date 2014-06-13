#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gather numeric information about the processed sequence data in an
MG-RAST project.
"""
from metaGTools.mgrast.api import mgrast_request, MGRASTException
import argparse
from collections import namedtuple
import json

STAT_FIELDS = ['raw_seq_count', 'failed_qc', 'passed_qc',
               'protein_coding_regions', 'predicted_prot_features',
               'identified_prot_features', 'identified_functional_categories',
               'ORFans']
STAT_FIELD_NAMES = ['Raw Sequence Count', 'Failed QC', 'Passed QC',
                    'Protein Coding Regions', 'Predicted Protein Features',
                    'Identified Protein Features',
                    'Identified Functional Categories', 'ORFans']
MetagenomeStats = namedtuple('MetagenomeStats', STAT_FIELDS)

def metagenome_project_stats(project_id, auth_key=None):
    """
    Given a project ID, download the overall project information from the
    MG-RAST API and store the data of interest. See: MetagenomeStats
    """
    try:
        req = mgrast_request('project', 'mgp'+project_id, {'verbosity':'full'},
                             auth_key)
    except MGRASTException as mgrast_ex:
        print 'ERROR:', mgrast_ex.message
        return

    project_data = json.loads(req.text)
    project_stats = {}

    for mg_id in [mg[0] for mg in project_data['metagenomes']]:
        req = mgrast_request('metagenome', mg_id, {'verbosity': 'stats'},
                             auth_key)
        mg_info = json.loads(req.text)
        mg_ss = mg_info['statistics']['sequence_stats']
        stats = MetagenomeStats(int(mg_ss['sequence_count_raw']),
                                int(mg_ss['sequence_count_raw']) - int(mg_ss['sequence_count_preprocessed']),
                                int(mg_ss['sequence_count_preprocessed']),
                                int(mg_ss['read_count_processed_aa']),
                                int(mg_ss['sequence_count_processed_aa']),
                                int(mg_ss['sequence_count_sims_aa']),
                                int(mg_ss['sequence_count_ontology']),
                                int(mg_ss['sequence_count_processed_aa']) - int(mg_ss['sequence_count_sims_aa']))
        project_stats[mg_id] = mg_info['name'], stats
    return project_stats


def join_stats(join_on, mg_stats):
    """
    Given multiple MetagenomeStats objects and a list of strings to match,
    merge the stats objects additively into a single grouped stat representing
    all the input data together.
    """
    new_stats = {}

    def add_metagenome_stats(new_mgs, old_mgs):
        return MetagenomeStats(*[getattr(new_mgs, f) + getattr(old_mgs, f) for f in old_mgs._fields])

    for mgs in mg_stats:
        # find maximally matching join criterion
        max_match = 0
        group = ''
        for grp in join_on:
            if grp in mgs[0] and len(grp) > max_match:
                max_match = len(grp)
                group = grp

        new_stats[group] = mgs[1] if group not in new_stats else add_metagenome_stats(mgs[1], new_stats[group])
    return new_stats


def write_stats_table(project_stats, out_fp):
    """
    Given a list of tuples (name, MetagenomeStats) write out to a tab-separated value
    file with columns ordered by name.
    """
    from operator import itemgetter

    with open(out_fp, 'w') as out_f:
        names = []
        all_stats = []
        for name, stats in sorted(project_stats.items(), key=itemgetter(0)):
            names.append(name)
            all_stats.append(stats)
        out_f.write('\t' + '\t'.join(names) + '\n')
        for i in range(len(all_stats[0])):
            line = []
            for j in range(len(all_stats)):
                line.append(str(all_stats[j][i]))
            out_f.write('{}\t{}\n'.format(STAT_FIELD_NAMES[i], '\t'.join(line)))


def handle_program_options():
    """Parses the given options passed in at the command line."""
    parser = argparse.ArgumentParser(description="Gather numeric information \
                                     about the processed sequence data in an \
                                     MG-RAST project.")
    parser.add_argument('project_id',
                        help="The project identifier (MG-RAST ID)")
    parser.add_argument('-a', '--auth_key',
                        help="An MG-RAST API authorization key. This is \
                        necessary to access projects marked as private.")
    parser.add_argument('-g', '--group_by', action='append',
                        help="A string that matches some part of the \
                              'Metagenome Name' field. All matching project \
                              metagenomes will be grouped by this identifier \
                              and their stats will be summed. This option can \
                              be specified multiple times to create multiple \
                              groups. All non-matching metagenomes will \
                              appear separately in the table. NOTE: \
                              Strings will be matched longest first. This \
                              allows for matching names that might be a \
                              substring of another match. For example: -g S \
                              -g NS. The name field will first be matched \
                              against the longest string (NS) first and then \
                              each smaller string in order.")
    parser.add_argument('-o', '--output_filename', default='meta_stats.txt',
                        help="The name of the file the project summary \
                        information will be written to.")

#    parser.add_argument('-v', '--verbose', action='store_true')

    return parser.parse_args()


def main():
    """Program entry point"""
    args = handle_program_options()

    mt_proj = metagenome_project_stats(args.project_id, args.auth_key)
    if mt_proj is None:
        return
    grouped_stats = join_stats(args.group_by, mt_proj.values())
    write_stats_table(grouped_stats.items(), args.output_filename)


if __name__ == "__main__":
    main()
