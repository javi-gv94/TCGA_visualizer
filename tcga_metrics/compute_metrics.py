from __future__ import division
import io
import os
import pandas
import math
import json
from argparse import ArgumentParser


def main(args):

    # input parameters
    input_participant = args.participant_data
    gold_standards_dir = args.metrics_ref
    cancer_types = args.cancer_types
    participant = args.participant_name
    out_dir = args.output
    
    # Assuring the output directory does exist
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    compute_metrics(input_participant,  gold_standards_dir, cancer_types, participant, out_dir)



def compute_metrics(input_participant,  gold_standards_dir, cancer_types, participant, out_dir):

    # get participant dataset
    participant_data = pandas.read_csv(input_participant, sep='\t',
                                       comment="#", header=0)
    
    # filter data by q-value
    if participant == "MutSig2CV":

        filtered_data = participant_data.loc[participant_data['qvalue'] <= 0.1]

        predicted_genes = filtered_data.iloc[:, 0].values

    elif participant == "ActiveDriver":

        filtered_data = participant_data.loc[participant_data['qvalue'] <= 0.0001]

        predicted_genes = filtered_data.iloc[:, 0].values

    elif participant == "MuSiC":

        filtered_data = participant_data.loc[participant_data['pvalue'] <= math.exp(-8)]
        filtered_data = filtered_data[filtered_data['info'] == "FILTER=PASS"]

        predicted_genes = filtered_data.iloc[:, 0].values

    else:

        filtered_data = participant_data.loc[participant_data['qvalue'] <= 0.05]

        predicted_genes = filtered_data.iloc[:, 0].values
    
    
    for cancer in cancer_types:
        # get metrics dataset
        metrics_data = pandas.read_csv(os.path.join(gold_standards_dir, cancer + ".txt"),
                                       comment="#", header=None)
        gold_standard = metrics_data.iloc[:, 0].values


        # TRUE POSITIVE RATE
        overlapping_genes = set(predicted_genes).intersection(gold_standard)
        TPR = len(overlapping_genes) / len(gold_standard)

        # ACCURACY/ PRECISION
        if len(predicted_genes) == 0:
            acc = 0
        else:
            acc = len(overlapping_genes) / len(predicted_genes)

        assessment_data = {'toolname': participant, 'x': TPR, 'y': acc, 'e': 0, 'cancer_type': cancer}

        with io.open(os.path.join(out_dir, cancer + "_" + participant + "_assessment.json"), mode='w', encoding="utf-8") as f:
            jdata = json.dumps(assessment_data, sort_keys=True, indent=4, separators=(',', ': '))
            f.write(unicode(jdata,"utf-8"))


if __name__ == '__main__':
    
    parser = ArgumentParser()
    parser.add_argument("-i", "--participant_data", help="list of cancer genes prediction", required=True)
    parser.add_argument("-c", "--cancer_types", nargs='+', help="list of types of cancer selected by the user, separated by spaces", required=True)
    parser.add_argument("-m", "--metrics_ref", help="dir that contains metrics reference datasets for all cancer types", required=True)
    parser.add_argument("-p", "--participant_name", help="name of the tool used for prediction", required=True)
    parser.add_argument("-o", "--output", help="output directory where assessment JSON files will be written", required=True)
    
    args = parser.parse_args()
    
    main(args)



