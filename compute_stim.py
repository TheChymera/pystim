#!/usr/bin/env python
__author__ = 'Horea Christian'

import numpy as np
import pandas as pd
from numpy.random import permutation, choice, sample
from os import path, listdir
from itertools import product
from data_functions import get_config_file, save_pd_csv, save_gen_csv
from routines import harari 

config = get_config_file()

#IMPORT VARIABLES
sequence_name = config.get('Files', 'sequence_name')
output_subdir = config.get('Directories', 'output_subdir')
stimuli_dir = config.get('Directories', 'stimuli_dir')
templates_dir = config.get('Directories', 'templates_dir')
scrambling_id = config.get('Decoding', 'scrambling_id')
scrambling_a_id = config.get('Decoding', 'scrambling_a_id')
scrambling_b_id = config.get('Decoding', 'scrambling_b_id')
fearful_id = config.get('Decoding', 'fearful_id')
happy_id = config.get('Decoding', 'happy_id')
female_id = config.get('Decoding', 'female_id')
male_id = config.get('Decoding', 'male_id')
easy_em_id = config.get('Decoding', 'easy_em_id')
hard_em_id = config.get('Decoding', 'hard_em_id')
scrambling_steps_id = [int(i) for i in config.get('Decoding', 'scrambling_steps_id').split(',')]
scrambling_steps_prefix = config.get('Decoding', 'scrambling_steps_prefix')
make_blocks = config.getboolean('Parameters', 'make_blocks')
block_size = config.getint('Parameters', 'block_size')
output_format = config.get('Parameters', 'output_format')
#END IMPORT VARIABLES

scrambling_steps_id_withprefix = [scrambling_steps_prefix+str(i) for i in scrambling_steps_id]
local_dir = path.dirname(path.realpath(__file__)) + '/' 
output_dir = local_dir + output_subdir
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
for variable_categories in product(scrambling_steps_id_withprefix, [[scrambling_a_id, scrambling_b_id]]):
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
for scrambling_step in scrambling_steps_id_withprefix:
    sequence.ix[(sequence['top face'].map(lambda x: scrambling_step in x)), 'scrambling'] = int(scrambling_step.strip('cell'))
sequence.ix[(sequence['top face'].map(lambda x: scrambling_id not in x)), 'scrambling'] = 0
#make blocks
if make_blocks:
    block_number = 0 #start value for iteration
    for step in range(0, len(sequence)*block_size, block_size):
        sequence.ix[step:step+block_size,'block'] = block_number
        block_number +=1

if output_format == 'christian':
    output_file = output_dir + sequence_name
    save_pd_csv(sequence, output_file)
elif output_format == 'gabriela':
    tamplate_subdir = output_format + '/'
    header = open(local_dir+templates_dir+tamplate_subdir+'header.txt', 'r')
    footer = open(local_dir+templates_dir+tamplate_subdir+'footer.txt', 'r')
    module = open(local_dir+templates_dir+tamplate_subdir+'module.txt', 'r')
    
    files_list = [easy_em_id, hard_em_id, ]
    output_file = output_dir + sequence_name + '_' + output_format + '.csv'
    with save_gen_csv(output_file) as outfile:
        outfile.write(header.read())
        
        outfile.write(footer.read())


