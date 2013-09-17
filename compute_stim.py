#!/usr/bin/env python
__author__ = 'Horea Christian'

import numpy as np
import pandas as pd
from numpy.random import permutation, choice, sample
from os import path, listdir
from itertools import product

from lefunctions import save_pd_csv
from routines import harari 

# General parameters:
sequence_name = 'faceRT_blocksize4'
output_subdir = 'sequences/'
stimuli_dir = '~/src/faceRT/img/px0'
scrambling_id = 'rand' #identifies scrambled files
scrambling_a_id = '_a.j' #first scrambling versions
scrambling_b_id = '_b.j' #second scrambling versions
fearful_id = '_FE_' #fearful faces
happy_id = '_HA_' #happy faces
female_id = 'F_'
male_id = 'M_'
easy_em_id = 'C100'
hard_em_id = 'C040'
scrambling_steps_id = ['cell6', 'cell10', 'cell14', 'cell18', 'cell22']
block_size = 4

local_dir = path.dirname(path.realpath(__file__)) + '/' 
output_dir = local_dir + output_subdir
output_file = output_dir + sequence_name
stimuli_dir = path.expanduser(stimuli_dir) # expands the path if it is specified with tilde for "home"
stimlist = permutation(listdir(stimuli_dir))
sequence = pd.DataFrame([]) # blank dataframe to add the stimuli lists to 


# 100% emotion trials
for variable_categories in product([male_id, female_id], [[happy_id, fearful_id],[fearful_id,happy_id]]):
    top_stimuli = [a for a in stimlist if variable_categories[0] in a and variable_categories[1][0] in a and easy_em_id in a and scrambling_id not in a]
    distractors = [a for a in stimlist if variable_categories[0] in a and variable_categories[1][1] in a and easy_em_id in a and scrambling_id not in a]
    subsequence = harari(top_stimuli, top_stimuli, distractors, suffix_characters=11) # with suffix identifier skipping because we don't want the same person twice in a slide
    sequence = pd.concat([sequence, subsequence], ignore_index=True)

# 40% emotion trials
for variable_categories in product([male_id, female_id], [[happy_id, fearful_id],[fearful_id,happy_id]]):
    top_stimuli = [a for a in stimlist if variable_categories[0] in a and variable_categories[1][0] in a and easy_em_id in a and scrambling_id not in a]
    distractors = [a for a in stimlist if variable_categories[0] in a and variable_categories[1][1] in a and hard_em_id in a and scrambling_id not in a]
    targets = [a for a in stimlist if variable_categories[0] in a and variable_categories[1][0] in a and hard_em_id in a and scrambling_id not in a]
    subsequence = harari(top_stimuli, targets, distractors, suffix_characters=11) # with suffix identifier skipping because we don't want the same person twice in a slide
    sequence = pd.concat([sequence, subsequence], ignore_index=True)
    
# scrambling trials
for variable_categories in product(scrambling_steps_id, [[scrambling_a_id, scrambling_b_id]]):
    top_stimuli = [a for a in stimlist if variable_categories[0] in a and variable_categories[1][0] in a and easy_em_id in a]
    distractors = [a for a in stimlist if variable_categories[0] in a and variable_categories[1][0] in a and easy_em_id in a]
    for idx, i in enumerate(distractors):
        distractors[idx] = distractors[idx][:-5]+'b.jpg'
    targets = top_stimuli # we use identical images for identification
    subsequence = harari(top_stimuli, targets, distractors, forbid_identical_targets=False)
    sequence = pd.concat([sequence, subsequence], ignore_index=True)

# Fill out meta-fileds
sequence.ix[(sequence['top face'].map(lambda x: happy_id in x)), 'emotion'] = 'happiness'
sequence.ix[(sequence['top face'].map(lambda x: fearful_id in x)), 'emotion'] = 'fear'
sequence.ix[(sequence['right face'].map(lambda x: easy_em_id in x)), 'emotion intensity'] = 100 # the top face is always C100
sequence.ix[(sequence['right face'].map(lambda x: hard_em_id in x)), 'emotion intensity'] = 40 # the top face is always C100
sequence.ix[(sequence['top face'].map(lambda x: male_id in x)), 'gender'] = 'm'
sequence.ix[(sequence['top face'].map(lambda x: female_id in x)), 'gender'] = 'f'
for scrambling_step in scrambling_steps_id:
    sequence.ix[(sequence['top face'].map(lambda x: scrambling_step in x)), 'scrambling'] = int(scrambling_step.strip('cell'))
sequence.ix[(sequence['top face'].map(lambda x: scrambling_id not in x)), 'scrambling'] = 0
#make blocks
block_number = 0 #start value for iteration
for step in range(0, len(sequence)*block_size, block_size):
    sequence.ix[step:step+block_size,'block'] = block_number
    block_number +=1
    
save_pd_csv(sequence, output_file)
