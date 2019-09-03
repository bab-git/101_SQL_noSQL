# %%
#while i < len(device_db):
#while i <= len(device_db):shab mi
#    i = 0
    #device_id = WK_list[i]['_id']    
    #  %%
#    i = device_db.loc[device_db['_id']==1054972,'_id'].index[0]
    device_id = int(device_db['_id'][i])
    print('Getting checks for device_id:',i,'/',len(device_db),'(%s)' % (device_db['device_name'][i]),'...')
#    device_id=int(device_db['_id'][device_db['device_name']=='SRV-PR-01'])
#    device_id = 1054972
#    del resultsd
    results = checks.find(
                {
                    "servertime":
                    {
                                    "$gte": datetime(2019,6,1,0,0,0),
                                    "$lte": datetime(2019,7,31,23,59,59)
                                    },    
                    "deviceid":device_id,
#                    "deviceid":1054972,
    #                "dsc247":2, 
                    "checkstatus": {"$ne":"testok"},
#                    "checkid": "26706789"
                }
                ,projection={'datetime': False}
                )
#    try:
    check_results = list(results)
#    except pymongo.errors.InvalidBSON:
#       print('year format prblem ==> skip the device')
#       i+=1
#       year_prob.append(device_id)
#       break
    #  %%
    len_fails = len(check_results)
    print('number of failed checks:',len_fails)
#  %%
    if len(check_results) == 0:
        i+=1
#        continue
    print('Prepaing the SQL table...')
    check_SQL=pd.DataFrame(check_results, columns = ['servertime','description',
                                                     'checkstatus','consecutiveFails','dsc247',
                                                     'extra','checkid','deviceid']).sort_values(by = 
#                                                        'servertime')#, ascending = False)
                                                    ['checkid','servertime'])#, ascending = False)                              
    temp = device_db.loc[i,['device_name','client_name','site_name','Type']]
    check_SQL[['device_name','client_name','site_name','Type']] = check_SQL.apply(lambda row: temp, axis = 1)      
    check_SQL = check_SQL.reset_index(drop = True)
    check_SQL['consFails'] = ''
    check_SQL['last_fail'] = ''
    check_SQL0 = check_SQL.copy()  # for debuging - todo remove
    
    check_current = check_SQL.loc[0,'checkid']
    check_SQL.loc[0,'consFails'] = check_SQL.loc[0,'consecutiveFails']
    check_SQL.loc[0,'last_fail'] = check_SQL.loc[0,'servertime']
    dsc247 = check_SQL['dsc247'][0]
   
    i_f = 1
 #  %%   loop over the rows
    while i_f < len(check_SQL):
#            if check_SQL['servertime'][i_f] >= datetime(2019,6,3,7,10,0):
#                break   
#  %%                 
        check_next = check_SQL.loc[i_f,'checkid']
#        if check_next == '26706789':
#            break        
        checkname = check_SQL.loc[i_f,'description']
        extra = check_SQL.loc[i_f,'extra']
        if H_annot(checkname,extra)=='ignore': # check-definite label 3 case
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
        else:  # new check            
            # adding new row
#                break
#                print('break')
            dsc247 = check_SQL['dsc247'][i_f]
            check_SQL.loc[i_f,'last_fail'] = check_SQL.loc[i_f,'servertime']
        
        if (check_next != check_current) | (seq == 0):
            # categorizing previous row#                
            checkname = check_SQL.loc[i_f-1,'description']
            extra = check_SQL.loc[i_f-1,'extra']
            pr = H_annot(checkname,extra)
            if pr == 'ignore':
                check_SQL = check_SQL.drop(i_f-1).reset_index(drop = True)
                i_f -= 1
#                    print('ignore')
            elif (pr=='nH')|(pr=='H'): # check-definite label H/N case
#                    break
                temp = check_SQL.loc[i_f-1,DB_col_list[:len(DB_col_list)-1]]
                temp['consecutiveFails'] = check_SQL.loc[i_f-1,'consFails']
                temp['Label'] = pr
                check_DB= check_DB.append(temp,ignore_index=True)
                check_SQL = check_SQL.drop(i_f-1).reset_index(drop = True)
                i_f -= 1
#                    print('Add')                    
#                    break                                        
                
        if check_SQL['consFails'][i_f]=='':
                check_SQL.loc[i_f,'consFails'] = check_SQL.loc[i_f,'consecutiveFails']
        check_current = check_next                
        i_f += 1
#  %%
    # Annotate last entry of SQL table  
    pr = H_annot(checkname,extra)
    if pr == 'ignore': # check-definite label 3 case
        check_SQL = check_SQL.drop(i_f-1).reset_index(drop = True)
    elif (pr=='nH')|(pr=='H'): # check-definite label H/N case
        temp = check_SQL.loc[i_f-1,DB_col_list[:len(DB_col_list)-1]]
        temp['consecutiveFails'] = check_SQL.loc[i_f-1,'consFails']
        temp['Label'] = pr
        check_DB= check_DB.append(temp,ignore_index=True)     
        check_SQL = check_SQL.drop(i_f-1).reset_index(drop = True)
    # %%        
            
    check_SQL_last = check_SQL[['device_name','Type','checkstatus',
                                'description','servertime','last_fail',
                                'client_name','site_name','extra',
                                'dsc247','deviceid','checkid','consFails']]
    check_SQL_last = check_SQL_last.rename(columns = {"consFails":"consecutiveFails"})
    check_SQL_last = check_SQL_last.sort_values(by = 'servertime')
        
    print('Saving', len(check_SQL_last), 'extracted failes to the SQL table...')        
    if not os.path.isfile(excel_path):
        check_SQL_last.to_excel(excel_path, index = False)
    else: # appending to the excell file
        book = load_workbook(excel_path)
        last_row = book['Sheet1'].max_row        
        writer = pd.ExcelWriter(excel_path, engine='openpyxl')        
#        writer = pd.ExcelWriter(excel_path)
#        check_SQL_last.to_excel(writer)
#        writer.save()        
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
        check_SQL_last.to_excel(writer, startrow = last_row+1,index = False, header = False)
        writer.save()
    print("""
          =========== tabel saved =====
          ============================="""
          )
    i += 1
    save_file = 'check_extraction.sav'
    pickle.dump({'device_i':i,'check_DB':check_DB}, open(save_file, 'wb'))
#    loaded_data = pickle.load( open(filename, "rb" ))
    