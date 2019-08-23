# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 12:30:47 2019

@author: Babak Hosseini
"""

#%%==================== Extracting trajectory data on demand
start_ind = 8    # start and end row indexes to be processed in the excell file
end_ind = 209
head_ind=7        # index of the header
excel_path = 'Checks list.xlsx' 
#book = load_workbook(excel_path)   
if os.path.isfile(excel_path):
    print('Reading data from the excel sheet...')
else:
    print("file not found") 
    
headers = pd.read_excel(excel_path, header = head_ind,nrows = 0 )
#np.where(fails_temp.columns=='Label')
#label_cl=list(fails_temp.columns).index('Label')
fails_select = pd.read_excel(excel_path, skiprows = start_ind-1,  nrows = end_ind-start_ind+1)
fails_select=fails_select.loc[fails_select['Label']==4]
fails_select=fails_select.fillna('')
fails_select=fails_select.loc[fails_select['last_fail']!=''].reset_index(drop = True)


get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]
#out_ind = get_indexes(4,label_list['Label'])
#excell_ind = np.array(out_ind) +start_ind
# %% Extraction loop
for row_ind in fails_select.index:
    print(row_data)
    
    
    

