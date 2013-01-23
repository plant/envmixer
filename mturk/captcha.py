'''
mturk/captcha.py
natural-mixer

2013 Brandon Mechtley
Arizona State University

Look through a Mechanical Turk results CSV file to verify that users passed the captcha. Every HIT
should have one or more test groups where the test sound is the same file as one of the source
sounds, so the similarity to the test sound should be maximum in these cases.
'''

import argparse
import prettytable as pt
import numpy as np

def verify(resultsfile):
    results = np.genfromtxt(resultsfile, delimiter='","', dtype=str)
    for i in range(len(results[0])):
        results[0,i] = results[0, i].strip('"')
    
    # Break up headers with .'s in them (Answer.*, Input.*)
    tokens = np.array([r.strip('"').split('.') for r in results[0]])
    
    # Columns that correspond to input filenames, slider answers (1-9), and descriptions,
    # respectively.
    cinputs = np.where([len(h) > 1 and h[1][0] == 'g' and h[0] == 'Input' for h in tokens])[0]
    canswers = np.where([len(h) > 1 and h[1][0] == 'g' and h[0] == 'Answer' for h in tokens])[0]
    cdesc = np.where([len(h) > 1 and h[1][0:2] == 'dg' and h[0] == 'Answer' for h in tokens])[0]
    
    # Individual column numbers for HIT ID, Worker ID, and Requester Feedback.
    chitid = np.where(results[0] == 'HITId')[0][0]
    cworkerid = np.where(results[0] == 'WorkerId')[0][0]
    cfeedback = np.where(results[0] == 'RequesterFeedback')[0][0]
    
    # List of all test/source sound ids in gXsY format.
    soundids = np.array([h[1] for h in tokens[cinputs]])
    
    # Reshape column IDs into groups for iteration over test groups.
    cinputs = cinputs.reshape((-1, 4))
    canswers = canswers.reshape((-1, 4))
    cdesc = cdesc.reshape((-1, 4))
    soundids = soundids.reshape((-1, 4))
    
    # Iterate through each group per each row.
    for i, row in enumerate(results[1:]):
        
        # Only bother providing output for HITs that have not been rejected.
        if not len(row[cfeedback]):
            for ginputs, ganswers, gdesc, gids in zip(cinputs, canswers, cdesc, soundids):
                inputs = row[ginputs]
                answers = row[ganswers]
                desc = row[gdesc]
                
                duplicates = inputs == inputs[0]
                
                # Find the CAPTCHA group.
                if np.sum(duplicates) > 1:
                    dupanswers = answers[duplicates]
                    
                    print '#'.join([
                        row[chitid].strip('"'),
                        row[cworkerid]] + \
                        [a.strip('"') for a in dupanswers] + \
                        [d.strip('\n') for d in desc[duplicates]]
                    )

if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description='Verify that Mechanical Turk workers have passed the captcha test.')
    parser.add_argument('results', metavar='csv', type=str, help='mturk results .csv file')
    args = parser.parse_args()
    
    verify(args.results)