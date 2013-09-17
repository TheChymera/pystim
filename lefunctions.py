def save_pd_csv(dataframe, filename): #save function which makes the target dir if it does not exist and backs up previous stim sequences
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
    dataframe.to_csv(filename+'.csv')
    
