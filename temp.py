def class_code(row_SQL):
    pr = 'ND'  #not determined
    
    #PING-Überprüfung
    if row_SQL['description'].find('PING-Überprüfung')>=0:
        if row_SQL['deviceid'] in {590715,801799,1090258}:
            pr = 'H'
        elif row_SQL['deviceid'] in {754547,620692}:
            pr = 'nH'
    elif row_SQL['description'].find('Ereignisprotokollüberprüfung')>=0 & row_SQL['description'].find('Backup')>=0:
        if row_SQL['extra'] == 'Ereignis nicht gefunden':
            pr = 'H'
        elif row_SQL['extra'].find('successfully')>=0:
            pr = 'ignore'        
            
            
    return pr

#------------------

head_ind = 8

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Keys/mongoDB_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Checks list").sheet1

sheet_g = Spread("Check evaluation")
sheet_g.open_sheet("Sheet1", create=False)   
sheet_g.sheet.resize(rows=head_ind)

headers = sheet.row_values(head_ind)
all_values = sheet.get_all_values()
check_SQL  = pd.DataFrame(all_values, columns = headers) 

all_checks = check_SQL.loc[range(head_ind,len(check_SQL)),'description'].unique()


#====== validation loop

DB_col_list = ['device_name','Type','checkstatus',
                                    'description','servertime','last_fail',
                                    'client_name','site_name','extra',
                                    'dsc247','deviceid','checkid','consecutiveFails',
                                    'Label']
i_dev = 0
# %%
while i_dev < len(device_db):
    device_id = int(device_db['_id'][i_dev])
    print('\nGetting checks for device_id:',i_dev,'/',len(device_db),'(%s)' % (device_db['device_name'][i_dev]),'...') 
    results = checks.find(
                {
                    "servertime":
                    {
                                    "$gte": datetime(2019,8,1,0,0,0),
                                    "$lte": datetime(2019,8,31,23,59,59)
                                    },    
                    "deviceid":device_id,
#                    "deviceid":1054972,
    #                "dsc247":2, 
                    "checkstatus": {"$ne":"testok"},
#                    "checkid": "26706789"
                }
                ,projection={'datetime': False}
                )
    check_results = list(results)
    
    len_fails = len(check_results)
    print('number of failed checks:',len_fails)
    if len(check_results) == 0:
        i_dev+=1
        continue
    print('Prepaing the SQL table...')
    check_SQL=pd.DataFrame(check_results, columns = ['servertime','description',
                                                     'checkstatus','consecutiveFails','dsc247',
                                                     'extra','checkid','deviceid']).sort_values(by = 
#                                                        'servertime')#, ascending = False)
                                                    ['checkid','servertime'])#, ascending = False)     
   
    temp = device_db.loc[i_dev,['device_name','client_name','site_name','Type']]
    check_SQL[['device_name','client_name','site_name','Type']] = check_SQL.apply(lambda row: temp, axis = 1)      
    check_SQL = check_SQL.reset_index(drop = True)
    check_SQL['consFails'] = ''
    check_SQL['last_fail'] = ''
    check_SQL['Label'] = ''
    check_SQL0 = check_SQL.copy()  # for debuging - todo remove
    
    check_current = check_SQL.loc[0,'checkid']
    check_SQL.loc[0,'consFails'] = check_SQL.loc[0,'consecutiveFails']
    check_SQL.loc[0,'last_fail'] = check_SQL.loc[0,'servertime']
    dsc247 = check_SQL['dsc247'][0]
   
    i_f = 1    
 #  %%   loop over the check-fail rows
    while i_f < len(check_SQL):        
        check_next = check_SQL.loc[i_f,'checkid']
        checkname = check_SQL.loc[i_f,'description']
        extra = check_SQL.loc[i_f,'extra']
        
#        if H_annot(checkname,extra) in {'ignore','nH'}: # check-definite label 1, 3 case
        pr1 = H_annot(checkname,extra)
        pr2 = class_code(check_SQL.loc[i_f])            
        if pr1 in {'ignore','nH'} or pr2 in {'ignore','nH'}: # check-definite label 1,3 case            
            check_SQL = check_SQL.drop(i_f).reset_index(drop = True)
            #                print('ignore')
#            print('continue')
            continue
                     
        if check_next == check_current:  # same check
            seq = 0  # flags the existing sequence

            a = check_SQL['last_fail'][i_f-1]
            b = check_SQL['servertime'][i_f]
            cons_b = check_SQL['consecutiveFails'][i_f]
            cons_a = check_SQL['consecutiveFails'][i_f-1]
            
            if ((b - a).total_seconds() < 3.5*3600): # 2-3hr consequative errors
                seq = 1
            elif (b.day-a.day == 1 or (b.day-a.day <0 and (b-a).total_seconds() < 24*3600) ): # next day sequence
                if dsc247 == 2 : # safety check or consecutiveFails
                    seq = 1
                else:    # look for in between testok!
                    
                    results = checks.find(
                                        {
                                            "servertime": {
                                                            "$gte": a,
                                                            "$lte": b
                                                            },    
                                            "deviceid":device_id,                                
                                            "checkstatus": "testok",
                                            "checkid": check_current                                            }
                                        )
                    temp_results = list(results)
                    if len(temp_results) == 0: # continues fail sequence
                        seq = 1
            if seq == 1:  # continues failing sequanece ==> clear it from the table    
                check_SQL.loc[i_f-1,'extra'] = check_SQL.loc[i_f,'extra']
                check_SQL = check_SQL.drop(i_f).reset_index(drop = True)
                i_f -= 1
                
            check_SQL.loc[i_f,'last_fail'] = b
            check_SQL.loc[i_f,'consFails'] = cons_b
#            check_SQL.loc[i_f,'extra'] = extra
        else:  # new check            
            # adding new row
#                break
#                print('break')
            dsc247 = check_SQL['dsc247'][i_f]
            check_SQL.loc[i_f,'last_fail'] = check_SQL.loc[i_f,'servertime']
        
        if (check_next != check_current) | (seq == 0):
#            raise ValueError('(check_next != check_current) | (seq == 0):')
            # categorizing previous row#                
            checkname = check_SQL.loc[i_f-1,'description']
            extra = check_SQL.loc[i_f-1,'extra']
                        
            pr1 = H_annot(checkname,extra)
            pr2 = class_code(check_SQL.loc[i_f])
            
            if pr1 in {'ignore','nH'} or pr2 in {'ignore','nH'}: # check-definite label 1,3 case
                check_SQL = check_SQL.drop(i_f-1).reset_index(drop = True)
                i_f -= 1
            else: # Nan or ND or H
#                raise ValueError('end i_f')
                if pr1 == 'ND' and pr2 == 'ND': # not check-definite label H/Nan case
                    if checkname in all_checks:
                        pr = 'nH'
                    else:
                        pr = 'new'
                else: # one of them is 'H' or 'Nan'
                    pr = list(filter(lambda pr: pr in {'H','Nan'}, [pr1,pr2]))[0]
                
                check_SQL.loc[i_f-1,'Label'] = pr
                
        if check_SQL['consFails'][i_f]=='':
                check_SQL.loc[i_f,'consFails'] = check_SQL.loc[i_f,'consecutiveFails']
        check_current = check_next                
        i_f += 1
#  %%
    # -------Annotate last entry of SQL table
#    raise ValueError('end i_f')
    i_f = len(check_SQL)-1
    checkname = check_SQL.loc[i_f,'description']
    extra = check_SQL.loc[i_f,'extra']
    
    pr1 = H_annot(checkname,extra)
    pr2 = class_code(check_SQL.loc[i_f])
        
    if pr1 in {'ignore','nH'} or pr2 in {'ignore','nH'}: # check-definite label 1,3 case
        check_SQL = check_SQL.drop(i_f).reset_index(drop = True)
    else: # Nan or ND or H
#        raise ValueError('end i_f')
        if pr1 == 'ND' and pr2 == 'ND': # not check-definite label H/Nan case
            if checkname in all_checks:
                pr = 'nH'
            else:
                pr = 'new'
        else: # one of them is 'H' or 'Nan'
            pr = list(filter(lambda pr: pr in {'H','Nan'}, [pr1,pr2]))[0]
                
        check_SQL.loc[i_f,'Label'] = pr
    #  %%        
            
    check_SQL_last = check_SQL[['device_name','Type','checkstatus',
                                'description','servertime','last_fail',
                                'client_name','site_name','extra',
                                'dsc247','deviceid','checkid','consFails','Label']]
    check_SQL_last = check_SQL_last.rename(columns = {"consFails":"consecutiveFails"})
    check_SQL_last = check_SQL_last.sort_values(by = 'servertime')
    
    
    #----------- save to server
    if len(check_SQL_last) == 0:
        print('0 checks remained to save to the excel file...')
        i_dev += 1
        continue
    
    raise ValueError('to save')
    
    sheet_g = Spread("Check evaluation")
    sheet_g.open_sheet("Sheet1", create=False)    
    
    last_row = sheet_g.sheet.row_count        
    sheet_g.df_to_sheet(check_SQL_last, index=False, headers = False,sheet='Sheet1', 
                        start=(last_row+2,1),  replace = False)
    
    print("""
          =========== tabel saved =====
          =============================
          """
          )
    i_dev += 1  