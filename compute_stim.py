#!/usr/bin/env python
__author__ = 'Horea Christian'


def main(output_format=False, scrambling_steps_id=False):
    import numpy as np
    import pandas as pd
    from numpy.random import permutation, choice, sample
    from os import path, listdir
    from itertools import product
    from data_functions import get_config_file, save_pd_csv, save_gen, save_pd_tsv
    from routines import hariri
    from string import Template
    
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
    if scrambling_steps_id:
        pass
    else: scrambling_steps_id = [int(i) for i in config.get('Decoding', 'scrambling_steps_id').split(',')]
    scrambling_steps_prefix = config.get('Decoding', 'scrambling_steps_prefix')
    make_blocks = config.getboolean('Parameters', 'make_blocks')
    block_size = config.getint('Parameters', 'block_size')
    if output_format:
        pass
    else: output_format = config.get('Parameters', 'output_format')
    keep_oldsequence = config.getboolean('Parameters', 'keep_oldsequence')
    #END IMPORT VARIABLES
    
    scrambling_steps_id_withprefix = [scrambling_steps_prefix+str(i) for i in scrambling_steps_id]
    local_dir = path.dirname(path.realpath(__file__)) + '/' 
    output_dir = local_dir + output_subdir

    if keep_oldsequence:
        if path.isfile(output_dir + '.' + sequence_name + 'last_exported_sequence'):
            sequence = pd.from_csv(output_dir + '.' + sequence_name + 'last_exported_sequence.csv')
        else: pass
    else:
        ### START CREATING THE NEW STIMLIST DATAFRAME
        scrambling_steps_id_withprefix = [scrambling_steps_prefix+str(i) for i in scrambling_steps_id]
        stimuli_dir = path.expanduser(stimuli_dir) # expands the path if it is specified with tilde for "home"
        stimlist = permutation(listdir(stimuli_dir))
        sequence = pd.DataFrame([]) # blank dataframe to add the stimuli lists to
        if make_blocks:
            sequence_name = sequence_name + '_' + str(block_size) + 'block'
        
        # 100% emotion trials
        for variable_categories in product([male_id, female_id], [[happy_id, fearful_id],[fearful_id,happy_id]]):
            top_stimuli = [a for a in stimlist if variable_categories[0] in a and variable_categories[1][0] in a and easy_em_id in a and scrambling_id not in a]
            distractors = [a for a in stimlist if variable_categories[0] in a and variable_categories[1][1] in a and easy_em_id in a and scrambling_id not in a]
            subsequence = hariri(top_stimuli, top_stimuli, distractors, suffix_characters=11) # with suffix identifier skipping because we don't want the same person twice in a slide
            sequence = pd.concat([sequence, subsequence], ignore_index=True)
        
        # 40% emotion trials
        for variable_categories in product([male_id, female_id], [[happy_id, fearful_id],[fearful_id,happy_id]]):
            top_stimuli = [a for a in stimlist if variable_categories[0] in a and variable_categories[1][0] in a and easy_em_id in a and scrambling_id not in a]
            distractors = [a for a in stimlist if variable_categories[0] in a and variable_categories[1][1] in a and hard_em_id in a and scrambling_id not in a]
            targets = [a for a in stimlist if variable_categories[0] in a and variable_categories[1][0] in a and hard_em_id in a and scrambling_id not in a]
            subsequence = hariri(top_stimuli, targets, distractors, suffix_characters=11) # with suffix identifier skipping because we don't want the same person twice in a slide
            sequence = pd.concat([sequence, subsequence], ignore_index=True)
            
        # scrambling trials
        for variable_categories in product(scrambling_steps_id_withprefix, [[scrambling_a_id, scrambling_b_id]]):
            top_stimuli = [a for a in stimlist if variable_categories[0] in a and variable_categories[1][0] in a and easy_em_id in a]
            distractors = [a for a in stimlist if variable_categories[0] in a and variable_categories[1][0] in a and easy_em_id in a]
            for idx, i in enumerate(distractors):
                distractors[idx] = distractors[idx][:-5]+'b.jpg'
            targets = top_stimuli # we use identical images for identification
            subsequence = hariri(top_stimuli, targets, distractors, forbid_identical_targets=False)
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
            
    # BEGIN OUTPUT FILE FORMATTING
    if 'christian' in output_format: # 'christian' format (dataframe, versatile, amongst others for faceRT)
        output_file = output_dir + sequence_name
        save_pd_csv(sequence, output_file)
    elif 'gabriela1' in output_format: # 'gabriela' format (for presentation)
        tamplate_subdir = output_format + '/'
        header = open(local_dir+templates_dir+tamplate_subdir+'header.txt', 'r').read()
        footer = open(local_dir+templates_dir+tamplate_subdir+'footer.txt', 'r').read()
        module = Template(open(local_dir+templates_dir+tamplate_subdir+'module.txt', 'r').read())
        #~ print module.substitute(name='a', t='a', l='a', r='a', N='a')
        
        for condition_file_id in ['cont_hard', 'cont_easy', 'em_hard', 'em_easy']:
            #START REMAP SOME VALUES
            sequence.ix[(sequence['correct answer'] == 'right'), 'correct answer'] = 1
            sequence.ix[(sequence['correct answer'] == 'left'), 'correct answer'] = 2
            #END REMAP SOME VALUES
            output_file = output_dir + sequence_name + '_' + output_format + '_' + condition_file_id
            with save_gen(output_file, extension='.txt') as outfile:
                outfile.write(header)
                if condition_file_id == 'cont_hard':
                    for idx, trial in sequence[(sequence['scrambling'] == scrambling_steps_id[0])].iterrows():
                        format_module(outfile, module, trial, idx)
                elif condition_file_id == 'cont_easy':
                    for idx, trial in sequence[(sequence['scrambling'] == scrambling_steps_id[1])].iterrows():
                        format_module(outfile, module, trial, idx)
                elif condition_file_id == 'em_hard':
                    for idx, trial in sequence[(sequence['scrambling'] == 0) & (sequence['emotion intensity'] == 40)].iterrows():
                        format_module(outfile, module, trial, idx)
                elif condition_file_id == 'em_easy':
                    for idx, trial in sequence[(sequence['scrambling'] == 0) & (sequence['emotion intensity'] == 100)].iterrows():
                        format_module(outfile, module, trial, idx)
                else: raise InputError('Your condition_file_id values do not correspond to the script\'s expectations.')
                outfile.write(footer)
    elif output_format == 'gabriela2':
        sequence['name'] = sequence['top face']
        for pos, le_name in enumerate(sequence['name']):
            sequence['name'].ix[pos] = path.splitext(le_name)[0] + ' ;'
        sequence.ix[(sequence['correct answer'] == 'right'), 'correct answer'] = 1
        sequence.ix[(sequence['correct answer'] == 'left'), 'correct answer'] = 2
        sequence = sequence.rename(columns={'top face': 'fname_up', 'left face': 'fname_down_left', 'right face': 'fname_down_right', 'correct answer': 'rating'})
        output_file = output_dir + sequence_name + '_' + output_format
        save_pd_tsv(sequence, output_file)
    output_file = output_dir + '.' + sequence_name + 'last_exported_sequence'
    save_pd_csv(sequence, output_file)
    # BEGIN OUTPUT FILE FORMATTING

def format_module(outfile, module, trial, idx):
    from os import path
    trial_name, _ = path.splitext(trial['top face'])
    outfile.write(module.substitute(name=trial_name, t=trial['top face'], l=trial['left face'], r=trial['right face']))
    
if __name__ == '__main__':
	main()
