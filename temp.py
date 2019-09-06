#import pandas as pd
#ind_add : the row under which the entry should be added!

i_check = 0
while i_check< len(sheet_checks):
    extra = sheet_checks['extra'][i_check]
    if extra == '':
        i_check +=1
        continue
    checkname = sheet_checks['description'][i_check]
    pr = H_annot(checkname,extra)
    
    if pr == 'ignore':
        print (i_check)
        raise ValueError('ignore')
        continue    
    
    elif (pr == 'H') | (pr == 'nH'):
        print (i_check)
        raise ValueError('H or nH')
        
        g_row = sheet.row_values(i_check+1)
        SQL_row = sheet_checks.iloc[i_check].values.tolist()
        SQL_row = list(filter(lambda x: x != '', SQL_row))
        
        if g_row != SQL_row:
            raise ValueError('SQL is not syncronized with google sheet \n update the SQL table from google-sheet')
        
        DB_col_list = check_DB.columns;
        
        
        deviceid = int(sheet_checks.loc[i_check,'deviceid'])
#        deviceid = 971448
#        checkid = '30016492'
        checkid = sheet_checks.loc[i_check,'checkid']
        time =  datetime.strptime(sheet_checks.loc[i_check,'servertime'], '%Y-%m-%d %H:%M:%S')
#        time = datetime(2019,7,5,15,43,16)
        
        dev_ind = check_DB['deviceid'] == deviceid
        chk_ind = check_DB['checkid'] == checkid
        tm_ind = check_DB['servertime'] > time
        
        if len(check_DB.loc[dev_ind].index) == 0:
            ind_add = len(check_DB) # to the end of list
        elif len(check_DB.loc[dev_ind & chk_ind].index) == 0:
            ind_add = check_DB.loc[dev_ind].index[0]-1  # to the top of device list
        elif len(check_DB.loc[dev_ind & chk_ind & tm_ind ].index) == 0:
            ind_add = check_DB.loc[dev_ind & chk_ind].index[0]-1  # to the top of device-check list
        else:            
            ind_add = check_DB.loc[dev_ind & chk_ind & tm_ind ].index[0]-1  # after the device-check happened before this one


        !!! HERE!!  check_DB imports lose their type!!!

               
        #--------- update check_DB                
        if ind_add == -1:
            ind_add =0
        check_DB1 = pd.DataFrame(check_DB.iloc[:ind_add+1])
        check_DB2 = pd.DataFrame(columns = DB_col_list)
        check_DB2.loc[0] = sheet_checks.loc[i_check,DB_col_list]
        check_DB2['Label'] = pr
        check_DB3 = pd.DataFrame(check_DB.iloc[ind_add+1:])
        check_DB = pd.concat([check_DB1, check_DB2, check_DB3],  ignore_index=True)
        

        
        #--------- update google sheet
        i_rmv = i_check
        if sheet_checks.loc[i_check+1,'deviceid'] == '':
            i_rmv = [i_check+1,i_check]
            for row in i_rmv:
                sheet.delete_row(row+1)
        else:
            sheet.delete_row(i_rmv+1)
                
        #--------- update local sheet
        sheet_checks = sheet_checks.drop(i_rmv).reset_index(drop = True)
        
        
        
        
#        save_file = 'check_extraction.sav'
        pickle.dump({'check_DB':check_DB}, open(load_file, 'wb'))
        continue
    
    i_check +=1