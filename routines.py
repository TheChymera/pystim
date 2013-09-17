#!/usr/bin/env python
__author__ = 'Horea Christian'

import numpy as np
import pandas as pd
from numpy.random import permutation, choice, sample

def harari(top_stimuli, targets, distractors, forbid_identical_targets=True, suffix_characters=0):
    randomness = list(permutation(np.tile([[True], [False]], (len(top_stimuli)/2,1)))) #generate balanced randomness for left/right target placing
    
    if forbid_identical_targets:
	if suffix_characters:
	    while True:
		targets = list(permutation(targets))
		distractors = list(permutation(distractors))
		errors = 0
		for i in range(len(targets)):
		    if targets[i][:-suffix_characters] == top_stimuli[i][:-suffix_characters] or distractors[i][:-suffix_characters] == top_stimuli[i][:-suffix_characters] or targets[i][:-suffix_characters] == distractors[i][:-suffix_characters]:
			errors =+1
		if errors == 0:
		    break	    
	else:
	    while targets[0] == top_stimuli[-1]: # avoid collisions when the last stimulus in the top_stimuli and target lists are the same
		targets = list(permutation(targets))
    distractors = distractors[::-1]
    targets = targets[::-1]
    stimseq = pd.DataFrame(index=np.arange(len(top_stimuli)), columns={'emotion': [], 'emotion intensity': [], 'scrambling': [], 'gender': [], 'top face': [], 'left face': [], 'right face': [], 'block': [], 'correct answer': []})
    stimseq['top face'] = top_stimuli
    for pos, top_stim in enumerate(stimseq['top face']):
	is_right = randomness.pop()
	if is_right:
	    stimseq['left face'].ix[pos] = distractors.pop()
	    stimseq['right face'].ix[pos] = targets.pop()
	    stimseq['correct answer'].ix[pos] = 'right'
	else:
	    stimseq['right face'].ix[pos] = distractors.pop()
	    stimseq['left face'].ix[pos] = targets.pop()
	    stimseq['correct answer'].ix[pos] = 'left'
    return stimseq
