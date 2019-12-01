import re
from datetime import date, timedelta
import numpy as np
import pandas as pd
from mailer import sendDiffMail
import tldextract

today = date.today()
delta = timedelta(days=1) #cerca il file di ieri
lastcheck = today-delta

try:
    current_file_path = f"internal_all_{today.day}{today.month}{today.year}.csv"
    previous_file_path = f"internal_all_{lastcheck.day}{lastcheck.month}{lastcheck.year}.csv"

    internal_all_previous = pd.read_csv(previous_file_path, low_memory=False)
    internal_all_current = pd.read_csv(current_file_path, low_memory=False)


    previous = internal_all_previous[internal_all_previous['Content'].str.contains("text/html", na=False)]
    current = internal_all_current[internal_all_current['Content'].str.contains("text/html", na=False)]

    _site = tldextract.extract(current['Address'].tolist()[0])
    site = '.'.join(_site[:])
    counters = {}

    ##newly pages
    _new_found_pages = pd.merge(previous,\
                                current,\
                                suffixes=('_prev', '_current'),\
                                on='Address',\
                                how='outer')

    _new_found_pages = _new_found_pages[_new_found_pages['Status Code_prev'].isna()]

    new_found_pages = _new_found_pages.filter(regex='Address|\_current') 
    counters['new_found_pages'] = len(_new_found_pages['Address'].tolist())

    ## newly lost

    _new_lost_pages = _new_found_pages[_new_found_pages['Status Code_current'].isna()]
    new_lost_pages = _new_lost_pages[_new_lost_pages.columns[_new_lost_pages.columns.to_series().str.contains('_prev')]]
    counters['new_lost_pages'] = len(_new_lost_pages['Address'].tolist())

    ## changed status code

    _changed_status_code = pd.merge(previous[['Address','Status Code']],\
                                    current[['Address','Status Code']],\
                                    suffixes=('_prev', '_current'),\
                                    on='Address',\
                                    how='inner')


    _changed_status_code['diff'] = np.where(_changed_status_code['Status Code_prev'] == _changed_status_code['Status Code_current'], 'no change', 'changed')

    changed_status_code = _changed_status_code[_changed_status_code['diff'] == 'changed']
    counters['changed_status_code'] = len(changed_status_code['Address'].tolist())
    ## changed indexation

    _changed_indexation = pd.merge(previous[['Address','Status Code', 'Indexability','Indexability Status']],\
                                current[['Address','Status Code', 'Indexability','Indexability Status']],\
                                suffixes=('_prev', '_current'), on='Address', how='inner')

    _changed_indexation['diff'] = np.where(_changed_indexation['Indexability_prev'] == _changed_indexation['Indexability_current'], 'no change', 'changed')

    changed_indexation = _changed_indexation[['Address','Indexability_prev','Indexability Status_prev','Indexability_current','Indexability Status_current','diff']]
    changed_indexation = changed_indexation[changed_indexation['diff'] == 'changed']
    counters['changed_indexation'] = len(changed_indexation['Address'].tolist())

    ## changed meta

    _changed_meta = pd.merge(previous[['Address','Title 1', 'Meta Description 1']],\
                                current[['Address','Title 1', 'Meta Description 1']],\
                                suffixes=('_prev', '_current'), on='Address', how='inner')


    _changed_meta['diff_title'] = np.where(_changed_meta['Title 1_prev'] == _changed_meta['Title 1_current'], 'no change', 'changed')

    _changed_meta['diff_desc'] = np.where(_changed_meta['Meta Description 1_prev'] == _changed_meta['Meta Description 1_current'], 'no change', 'changed')
    changed_title = _changed_meta[_changed_meta['diff_title'] == 'changed']
    changed_title = changed_title.dropna().filter(regex='Address|^Title.+|diff\_title')
    counters['changed_title'] = len(changed_title['Address'].tolist())

    changed_desc= _changed_meta[_changed_meta['diff_desc'] == 'changed']
    changed_desc = changed_desc.dropna().filter(regex='Address|.+Description.+|diff\_desc')
    counters['changed_desc'] = len(changed_desc['Address'].tolist())

    ## changed H1 tags

    changed_h1 = pd.merge(previous.filter(regex='Address|^H1\-\d{1,2}$').dropna(thresh=3),\
                            current.filter(regex='Address|^H1\-\d{1,2}$').dropna(thresh=3),\
                            suffixes=('_prev', '_current'),\
                            on='Address',\
                            how='inner')
    changed_h1.replace(np.nan, '', regex=True, inplace=True)

    changed_h1_cols = current.filter(regex='Address|^H1\-\d{1,2}$').dropna(thresh=3).columns.tolist()
    r = re.compile("^H1\-\d{1,2}")
    newlist = list(filter(r.match, changed_h1_cols))

    for i in range(1,len(newlist)+1):
        new_diff = "H1-"+str(i)
        new = f"{new_diff}_current"
        old = f"{new_diff}_prev"
        _tmp = f"diff-{new_diff}"
        changed_h1[_tmp] = changed_h1[new] != changed_h1[old]

    changed_h1.columns =[column.replace("-", "_") for column in changed_h1.columns] 
    diff_col_lst = changed_h1.filter(regex='diff\_H1').columns.tolist()
    exp = ' or '.join(diff_col_lst)
    changed_h1 = changed_h1.query(exp)

    counters['changed_h1'] = len(changed_h1['Address'].tolist())


    ## Changed H2

    changed_h2 = pd.merge(previous.filter(regex='Address|^H2\-\d{1,2}$').dropna(thresh=3),\
                    current.filter(regex='Address|^H2\-\d{1,2}$').dropna(thresh=3),\
                    suffixes=('_prev', '_current'),\
                    on='Address',\
                    how='inner')

    changed_h2.replace(np.nan, '', regex=True, inplace=True)
    changed_h2_cols = current.filter(regex='Address|^H2\-\d{1,2}$').dropna(thresh=3).columns.tolist()
    r = re.compile("^H2\-\d{1,2}")
    newlist = list(filter(r.match, changed_h2_cols))
    for i in range(1,len(newlist)+1):
        new_diff = "H2-"+str(i)
        new = f"{new_diff}_current"
        old = f"{new_diff}_prev"
        _tmp = f"diff-{new_diff}"
        changed_h2[_tmp] = changed_h2[new] != changed_h2[old]
    changed_h2.columns =[column.replace("-", "_") for column in changed_h2.columns] 
    diff_col_lst = changed_h2.filter(regex='diff\_H2').columns.tolist()
    exp = ' or '.join(diff_col_lst)
    changed_h2 = changed_h2.query(exp)

    counters['changed_h2'] = len(changed_h2['Address'].tolist())

    ## Changed canonical
    _changed_canonical = pd.merge(previous[['Address','Status Code','Canonical Link Element 1']],current[['Address','Status Code','Canonical Link Element 1']],\
                        suffixes=('_prev', '_current'), on='Address', how='inner')
    _changed_canonical.replace(np.nan, '', regex=True, inplace=True)
    _changed_canonical['diff_canonical'] = np.where(_changed_canonical['Canonical Link Element 1_prev'] == _changed_canonical['Canonical Link Element 1_current'], 'no change', 'changed')
    changed_canonical = _changed_canonical[_changed_canonical['diff_canonical'] == 'changed']
    
    counters['changed_canonicals'] = len(changed_canonical['Address'].tolist())
    
    ## Write to Excel
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    out_filename = f"diff_{today.day}{today.month}{today.year}_vs_{lastcheck.day}{lastcheck.month}{lastcheck.year}.xlsx"
    writer = pd.ExcelWriter(out_filename, engine='xlsxwriter', options={'strings_to_urls': False})

    # Write each dataframe to a different worksheet.
    new_found_pages.to_excel(writer, sheet_name='New Found Pages')
    new_lost_pages.to_excel(writer, sheet_name='New Lost Pages')
    changed_status_code.to_excel(writer, sheet_name='Changed Status Code')
    changed_indexation.to_excel(writer, sheet_name='Changed Indexation')
    changed_title.to_excel(writer, sheet_name='Changed Titles')
    changed_desc.to_excel(writer, sheet_name='Changed Description')
    changed_h1.to_excel(writer, sheet_name='Changed H1')
    changed_h2.to_excel(writer, sheet_name='Changed H2')
    changed_canonical.to_excel(writer, sheet_name='Changed Canonicals')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    # Send Mail
    if sum(counters.values()) == 0:
        print('NO changes detected!')
    else:
        sendDiffMail(site, out_filename, counters)
except FileNotFoundError:
    print("error!")