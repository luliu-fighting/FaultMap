"""This script runs all other scripts required for calculating a ranking

@author: St. Elmo Wilken, Simon Streicher

"""

from ranking.gaincalc import create_connectionmatrix
from ranking.gaincalc import calc_partialcor_gainmatrix
from ranking.formatmatrices import rankforward, rankbackward
from ranking.formatmatrices import split_tsdata
from ranking.noderank import calculate_rank
from ranking.noderank import create_blended_ranking
from ranking.noderank import calc_transient_importancediffs

import json
import csv
import numpy as np

# Load directories config file
dirs = json.load(open('config.json'))
# Get data and preferred export directories from directories config file
dataloc = dirs['dataloc']
saveloc = dirs['saveloc']
# Define plant and case names to run
plant = 'tennessee_eastman'
# Define plant data directory
plantdir = dataloc + 'plants/' + plant + '/'
cases = ['dist11_closedloop', 'dist11_closedloop_pressup', 'dist11_full',
         'presstep_closedloop', 'presstep_full']
# Load plant config file
caseconfig = json.load(open(plantdir + plant + '.json'))
# Get sampling rate
sampling_rate = caseconfig['sampling_rate']


def looprank_single(case):
    # Get the correlation and partial correlation matrices
    _, gainmatrix = \
        calc_partialcor_gainmatrix(connectionmatrix, tags_tsdata, dataset)
    np.savetxt(saveloc + "gainmatrix.csv", gainmatrix,
               delimiter=',')
    
    # TODO: The forward, backward and blended ranking will all be folded
    # into a single method, currently isolated for ease of access to
    # intermediate results
    forwardconnection, forwardgain, forwardvariablelist = \
        rankforward(variables, gainmatrix, connectionmatrix, 0.01)
    backwardconnection, backwardgain, backwardvariablelist = \
        rankbackward(variables, gainmatrix, connectionmatrix, 0.01)
    
    forwardrank = calculate_rank(forwardgain, forwardvariablelist)
    backwardrank = calculate_rank(backwardgain, backwardvariablelist)
    blendedranking, slist = create_blended_ranking(forwardrank, backwardrank,
                                                   variables, alpha=0.35)   
    
    with open(saveloc + case + '_importances.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for x in slist:
            writer.writerow(x)
#            print(x)
    print("Done with single ranking")

def looprank_transient(case, samplerate, boxsize, boxnum):
    # Split the tags_tsdata into sets (boxes) useful for calculating
    # transient correlations
    boxes = split_tsdata(tags_tsdata, dataset, samplerate,
                         boxsize, boxnum)
    # Calculate gain matrix for each box
    gainmatrices = [calc_partialcor_gainmatrix(connectionmatrix, box,
                                               dataset)[1]
                    for box in boxes]
    rankinglists = []
    rankingdicts = []
    for index, gainmatrix in enumerate(gainmatrices):
        # Store the gainmatrix
        np.savetxt(saveloc + case + "_gainmatrix_" + str(index) + ".csv",
                   gainmatrix, delimiter=',')
        # Get everything needed to calculate slist
        # TODO: remove clone between this and similar code found in
        # looprank_single
        forwardconnection, forwardgain, forwardvariablelist = \
            rankforward(variables, gainmatrix, connectionmatrix, 0.01)
        backwardconnection, backwardgain, backwardvariablelist = \
            rankbackward(variables, gainmatrix, connectionmatrix, 0.01)
    
        forwardrank = calculate_rank(forwardgain, forwardvariablelist)
        backwardrank = calculate_rank(backwardgain, backwardvariablelist)
        blendedranking, slist = create_blended_ranking(forwardrank,
                                                       backwardrank,
                                                       variables, alpha=0.35)
        rankinglists.append(slist)
        with open(saveloc + 'importances_' + str(index) + '.csv', 'wb') \
            as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for x in slist:
                writer.writerow(x)
    #            print(x)
        rankingdicts.append(blendedranking)
    
    print("Done with transient rankings")
    
    transientdict, basevaldict = \
        calc_transient_importancediffs(rankingdicts, variables)

for case in cases:
    # Get connection (adjacency) matrix
    connectionloc = (plantdir + 'connections/' +
                     caseconfig[case]['connections'])
    # Get time series data
    tags_tsdata = (plantdir + 'data/' +
                   caseconfig[case]['data'])
    # Get dataset name
    dataset = caseconfig[case]['dataset']
    # Get the variables and connection matrix
    [variables, connectionmatrix] = create_connectionmatrix(connectionloc)
    print "Number of tags: ", len(variables)
    boxnum = caseconfig[case]['boxnum']
    boxsize = caseconfig[case]['boxsize']    
    
    looprank_single(case)
    looprank_transient(case, sampling_rate, boxsize, boxnum)
    
    