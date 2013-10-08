__author__ = 'Horea Christian'

def save_csv(filename):
    from os import path, makedirs
    from shutil import move
    from datetime import date, datetime
    import pandas as pd
    jzt=datetime.now()
    time = str(date.today())+'_'+str(jzt.hour)+str(jzt.minute)+str(jzt.second)
    if path.isdir(path.dirname(filename)): 
		pass
    else:
		makedirs(path.dirname(filename))
    if path.isfile(filename + '.csv'):
        if path.isdir(path.dirname(filename)+'/.backup'):
            pass
        else: makedirs(path.dirname(filename)+'/.backup')        
        newname = path.dirname(filename)+'/.backup/'+path.basename(filename)+'_'+time
        move(filename+'.csv', newname+'.csv')
        print 'moved pre-existing data file '+ filename +'.csv to backup location ('+newname+'.csv)'
    else: pass
    
def save_pd_csv(dataframe, filename):
    save_csv(filename)
    dataframe.to_csv(filename+'.csv')

def save_gen_csv(filename):
    save_csv(filename)
    return open(filename, 'a')

def get_config_file():
	from os import listdir, path
	import ConfigParser
	#GET CONFIG FILE
	cfg_file = filter(lambda x: x.endswith('.cfg'), listdir(path.dirname(path.realpath(__file__))))
	if len(cfg_file) > 1:
	    raise InputError('There are multiple *.cfg files in your experiment\'s rot directory (commonly .../faceRT/experiment) - Please delete all but one (whichever you prefer). The script will not run until then.')
	config = ConfigParser.ConfigParser()
	config.read(cfg_file)
	return config
	#END GET CONFIG FILE
