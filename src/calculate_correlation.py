from qc_utils import QCMetric, QCMetricRecord
import argparse
import json
import pandas as pd


def filter_genomic_transcripts(DF):
    not_genomic_transcript = DF.genomic_transcript != 'genomic_transcript'
    return DF[not_genomic_transcript]


def filter_startswith_TALON(DF):
    not_starts_with_TALON = DF['annot_gene_id'].apply(lambda x: not x.startswith('TALON'))
    return DF[not_starts_with_TALON]


def get_gene_counts(DF, colname):
    return DF.groupby(['annot_gene_id'])[colname].sum()


def main(args):
    rep1_abundance = pd.read_csv(args.rep1_abundance, sep='\t')
    rep2_abundance = pd.read_csv(args.rep2_abundance, sep='\t')
    rep1_filtered = filter_startswith_TALON(filter_genomic_transcripts(rep1_abundance))
    rep2_filtered = filter_startswith_TALON(filter_genomic_transcripts(rep2_abundance))
    del rep1_abundance
    del rep2_abundance
    rep1_counts = get_gene_counts(rep1_filtered, rep1_filtered.columns[-1])
    rep2_counts = get_gene_counts(rep2_filtered, rep2_filtered.columns[-1])
    del rep1_filtered
    del rep2_filtered
    aligned_counts = rep1_counts.align(rep2_counts, join='outer', fill_value=0)
    spearman = aligned_counts[0].corr(aligned_counts[1], method='spearman')
    spearman_qc = QCMetric('spearman_correlation', {'spearman_correlation': spearman})
    spearman_record = QCMetricRecord([spearman_qc])
    with open(args.outfile, 'w') as fp:
        json.dump(spearman_record.to_ordered_dict(), fp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rep1_abundance', type=str, help='.tsv file containing the abundance from rep1.')
    parser.add_argument('--rep2_abundance', type=str, help='.tsv file containing the abundance from rep2.')
    parser.add_argument('--outfile', type=str, help='output filename.')
    args = parser.parse_args()
    main(args)
