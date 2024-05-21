import pandas as pd
import pymysql
import re
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings
warnings.filterwarnings('ignore')

pymysql.version_info = (1, 3, 13, "final", 0)
pymysql.install_as_MySQLdb()
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='password123',
                       db='devices',
                       charset='utf8',
                       cursorclass=pymysql.cursors.DictCursor
                       )
cursor = conn.cursor()

def eval_substrate():
    cursor.execute("select from_pvk_db.Ref_DOI_number, from_pvk_db.Substrate, device_attributes.Substrate "
                   "from from_pvk_db, device_attributes where from_pvk_db.Ref_DOI_number = device_attributes.Ref_DOI_number")
    Substrate_result = cursor.fetchall()
    y_test = []
    y_pred = []
    for row in Substrate_result:
        pvk_db_Substrate = row['Substrate']
        mined_Substrate = row['device_attributes.Substrate']
        y_test.append(pvk_db_Substrate)
        y_pred.append(mined_Substrate)
    print('SUBSTRATE')
    print('Accuracy:', accuracy_score(y_test, y_pred))
    print('Precision (weighted, labels=np.unique(y_pred)):',
          precision_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('Recall (weighted):', recall_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('F1 score (weighted):', f1_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('--------------------------------------------------')

def eval_flexible():
    cursor.execute("select from_pvk_db.Ref_DOI_number, from_pvk_db.Cell_flexible, device_attributes.Cell_flexible "
                   "from from_pvk_db, device_attributes where from_pvk_db.Ref_DOI_number = device_attributes.Ref_DOI_number")
    flexible_result = cursor.fetchall()
    y_test = []
    y_pred = []
    for row in flexible_result:
        pvk_db_flexible = row['Cell_flexible']
        mined_flexible = row['device_attributes.Cell_flexible']
        y_test.append(pvk_db_flexible.lower())
        y_pred.append(mined_flexible.lower())
    print('CELL FLEXIBLE')
    print('Accuracy:', accuracy_score(y_test, y_pred))
    print('Precision (weighted, labels=np.unique(y_pred)):',
          precision_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('Recall (weighted):', recall_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('F1 score (weighted):', f1_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('--------------------------------------------------')

def eval_architecture():
    cursor.execute(
        "select from_pvk_db.Ref_DOI_number, from_pvk_db.Cell_architecture, device_attributes.Cell_architecture "
        "from from_pvk_db, device_attributes where from_pvk_db.Ref_DOI_number = device_attributes.Ref_DOI_number")
    architecture_result = cursor.fetchall()
    y_test = []
    y_pred = []
    count_none = 0
    for row in architecture_result:
        pvk_db_architecture = row['Cell_architecture']
        mined_architecture = row['device_attributes.Cell_architecture']
        if (pvk_db_architecture == 'pin' or pvk_db_architecture == 'nip') and mined_architecture != '':
            y_test.append(pvk_db_architecture.lower())
            y_pred.append(mined_architecture.lower())
        else:
            count_none += 1
    print('CELL ARCHITECTURE')
    print('Accuracy:', accuracy_score(y_test, y_pred))
    print('Precision (weighted, labels=np.unique(y_pred)):',
          precision_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('Recall (weighted):', recall_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('F1 score (weighted):', f1_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('none: ' + str(count_none))
    print('--------------------------------------------------')

def eval_ETL():
    cursor.execute("select from_pvk_db.Ref_DOI_number, from_pvk_db.ETL, device_attributes.ETL "
                   "from from_pvk_db, device_attributes where from_pvk_db.Ref_DOI_number = device_attributes.Ref_DOI_number")
    ETL_result = cursor.fetchall()
    y_test = []
    y_pred = []
    for row in ETL_result:
        pvk_db_ETL = row['ETL'].lower()
        mined_ETL = row['device_attributes.ETL'].lower()
        if pvk_db_ETL == 'none':
            continue
        if 'pcbm' in pvk_db_ETL:
            pvk_db_ETL = 'pcbm'
        if 'pcbm' in mined_ETL or 'pc61bm' in mined_ETL or 'pc60bm' in mined_ETL:
            mined_ETL = 'pcbm'
        if 'sno2' in pvk_db_ETL:
            pvk_db_ETL = 'sno2'
        if 'sno2' in mined_ETL:
            mined_ETL = 'sno2'
        if 'tio2' in pvk_db_ETL:
            pvk_db_ETL = 'tio2'
        if 'tio2' in mined_ETL:
            mined_ETL = 'tio2'
        if 'zno' in pvk_db_ETL:
            pvk_db_ETL = 'zno'
        if 'zno' in mined_ETL:
            mined_ETL = 'zno'
        if '|' in pvk_db_ETL:
            l = pvk_db_ETL.split('|')
            pvk_db_ETL = l[0].rstrip().lstrip()
        y_test.append(pvk_db_ETL)
        y_pred.append(mined_ETL)
    print('ETL')
    print('Accuracy:', accuracy_score(y_test, y_pred))
    print('Precision (weighted, labels=np.unique(y_pred)):', precision_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('Recall (weighted, labels=np.unique(y_pred):', recall_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('F1 score (weighted, labels=np.unique(y_pred):', f1_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('--------------------------------------------------')

def eval_HTL():
    cursor.execute("select from_pvk_db.Ref_DOI_number, from_pvk_db.HTL, device_attributes.HTL from from_pvk_db, device_attributes where from_pvk_db.Ref_DOI_number = device_attributes.Ref_DOI_number")
    HTL_result = cursor.fetchall()
    y_test = []
    y_pred = []
    for row in HTL_result:
        pvk_db_HTL = row['HTL'].lower()
        mined_HTL = row['device_attributes.HTL'].lower()
        if pvk_db_HTL == 'none':
            continue
        if 'spiro-meotad' in pvk_db_HTL or 'spiro-ometad' in pvk_db_HTL:
            pvk_db_HTL = 'spiro-ometad'
        if 'spiro-meotad' in mined_HTL or 'spiro-ometad' in mined_HTL:
            mined_HTL = 'spiro-ometad'
        if 'nio' in pvk_db_HTL:
            pvk_db_HTL = 'nio'
        if 'nio' in mined_HTL:
            mined_HTL = 'nio'
        if '|' in pvk_db_HTL:
            l = pvk_db_HTL.split('|')
            pvk_db_HTL = l[0].rstrip().lstrip()
        y_test.append(pvk_db_HTL)
        y_pred.append(mined_HTL)
    print('HOLE TRANSPORT LAYER')
    print('Accuracy:', accuracy_score(y_test, y_pred))
    print('Precision (weighted, labels=np.unique(y_pred)):', precision_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('Recall (weighted):', recall_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('F1 score (weighted):', f1_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('--------------------------------------------------')

def eval_pvk_short_form():
    cursor.execute("select from_pvk_db.Ref_DOI_number, from_pvk_db.Perovskite_composition_short_form, "
                   "device_attributes.Perovskite_composition_short_form, device_attributes.Perovskite_composition "
                   "from from_pvk_db, device_attributes where from_pvk_db.Ref_DOI_number = device_attributes.Ref_DOI_number")
    Perovskite_composition_short_form_result = cursor.fetchall()
    y_test = []
    y_pred = []
    count_one = 0
    count_none = 0
    for row in Perovskite_composition_short_form_result:
        pvk_db_Perovskite_composition_short_form = row['Perovskite_composition_short_form']
        mined_Perovskite_composition_short_form = row['device_attributes.Perovskite_composition_short_form']
        pvk_db_arranged = ''
        mined_arranged = ''
        ions = ['GU', 'BA', 'PEA', 'Cs', 'FA', 'MA', 'Pb', 'Sn', 'Ge', 'Bi', 'Ag', 'Na', 'Br', 'Cl', 'I', 'SCN']
        for ion in ions:
            if ion in pvk_db_Perovskite_composition_short_form:
                pvk_db_arranged += ion
            if ion in mined_Perovskite_composition_short_form:
                mined_arranged += ion
        if pvk_db_arranged != '' and mined_arranged != '':
            y_test.append(pvk_db_arranged)
            y_pred.append(mined_arranged)
            count_one += 1
        else:
            count_none += 1
    print('PVK SHORT FORM')
    print('Accuracy:', accuracy_score(y_test, y_pred))
    print('Precision (weighted, labels=np.unique(y_pred)):',
          precision_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('Recall (weighted):',
          recall_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('F1 score (weighted):',
          f1_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('not none:' + str(count_one))
    print('none:' + str(count_none))
    print('--------------------------------------------------')

def eval_pvk_long_form():
    cursor.execute("select from_pvk_db.Ref_DOI_number, "
                   "from_pvk_db.Perovskite_composition_a_ions, device_attributes.Perovskite_composition_a_ions, "
                   "from_pvk_db.Perovskite_composition_b_ions, device_attributes.Perovskite_composition_b_ions, "
                   "from_pvk_db.Perovskite_composition_c_ions, device_attributes.Perovskite_composition_c_ions, "
                   "from_pvk_db.Perovskite_composition_a_ions_coefficients, device_attributes.Perovskite_composition_a_ions_coefficients, "
                   "from_pvk_db.Perovskite_composition_b_ions_coefficients, device_attributes.Perovskite_composition_b_ions_coefficients, "
                   "from_pvk_db.Perovskite_composition_c_ions_coefficients, device_attributes.Perovskite_composition_c_ions_coefficients "
                   "from from_pvk_db, device_attributes where from_pvk_db.Ref_DOI_number = device_attributes.Ref_DOI_number")
    Perovskite_ions = cursor.fetchall()
    correct = 0
    wrong = 0
    for row in Perovskite_ions:
        if '|' not in row['Perovskite_composition_a_ions_coefficients'] != '' and 'x' not in row[
            'Perovskite_composition_a_ions_coefficients'] != '' \
                and 'x' not in row['Perovskite_composition_c_ions_coefficients'] != '' and row[
            'device_attributes.Perovskite_composition_a_ions'] != '':
            pvk_db_a = dict(sorted(dict(zip(row['Perovskite_composition_a_ions'].split('; '),
                                            ['%.2f' % float(elem) for elem in
                                             row['Perovskite_composition_a_ions_coefficients'].split('; ')])).items()))
            pvk_db_Perovskite_composition_a_ions = pvk_db_a.keys()
            pvk_db_Perovskite_composition_a_ions_coefficients = ['%.2f' % float(elem) for elem in pvk_db_a.values()]
            mined_a = dict(sorted(dict(
                zip(row['device_attributes.Perovskite_composition_a_ions'].split(', '),
                    ['%.2f' % float(elem) for elem in
                     row['device_attributes.Perovskite_composition_a_ions_coefficients'].split(
                         ', ')])).items()))
            mined_Perovskite_composition_a_ions = mined_a.keys()
            mined_Perovskite_composition_a_ions_coefficients = ['%.2f' % float(elem) for elem in mined_a.values()]
            pvk_db_b = dict(sorted(dict(zip(row['Perovskite_composition_b_ions'].split('; '),
                                            ['%.2f' % float(elem) for elem in
                                             row['Perovskite_composition_b_ions_coefficients'].split('; ')])).items()))
            pvk_db_Perovskite_composition_b_ions = pvk_db_b.keys()
            pvk_db_Perovskite_composition_b_ions_coefficients = ['%.2f' % float(elem) for elem in pvk_db_b.values()]
            mined_b = dict(sorted(dict(
                zip(row['device_attributes.Perovskite_composition_b_ions'].split(', '),
                    ['%.2f' % float(elem) for elem in
                     row['device_attributes.Perovskite_composition_b_ions_coefficients'].split(
                         ', ')])).items()))
            mined_Perovskite_composition_b_ions = mined_b.keys()
            mined_Perovskite_composition_b_ions_coefficients = ['%.2f' % float(elem) for elem in mined_b.values()]
            pvk_db_c = dict(sorted(dict(zip(row['Perovskite_composition_c_ions'].split('; '),
                                            ['%.2f' % float(elem) for elem in
                                             row['Perovskite_composition_c_ions_coefficients'].split('; ')])).items()))
            pvk_db_Perovskite_composition_c_ions = pvk_db_c.keys()
            pvk_db_Perovskite_composition_c_ions_coefficients = ['%.2f' % float(elem) for elem in pvk_db_c.values()]
            mined_c = dict(sorted(dict(
                zip(row['device_attributes.Perovskite_composition_c_ions'].split(', '),
                    ['%.2f' % float(elem) for elem in
                     row['device_attributes.Perovskite_composition_c_ions_coefficients'].split(
                         ', ')])).items()))
            mined_Perovskite_composition_c_ions = mined_c.keys()
            mined_Perovskite_composition_c_ions_coefficients = ['%.2f' % float(elem) for elem in mined_c.values()]

            if (pvk_db_Perovskite_composition_a_ions == mined_Perovskite_composition_a_ions) \
                    and (pvk_db_Perovskite_composition_b_ions == mined_Perovskite_composition_b_ions) \
                    and (pvk_db_Perovskite_composition_c_ions == mined_Perovskite_composition_c_ions) \
                    and (pvk_db_Perovskite_composition_a_ions_coefficients == mined_Perovskite_composition_a_ions_coefficients) \
                    and (pvk_db_Perovskite_composition_b_ions_coefficients == mined_Perovskite_composition_b_ions_coefficients) \
                    and (pvk_db_Perovskite_composition_c_ions_coefficients == mined_Perovskite_composition_c_ions_coefficients):
                correct += 1
            else:
                wrong += 1

    print('PVK LONG FORM')
    print('Accuracy:', str(correct / (correct + wrong)))
    print('--------------------------------------------------')

def eval_pvk_ions():
    cursor.execute("select from_pvk_db.Ref_DOI_number, "
                   "from_pvk_db.Perovskite_composition_a_ions, device_attributes.Perovskite_composition_a_ions, "
                   "from_pvk_db.Perovskite_composition_b_ions, device_attributes.Perovskite_composition_b_ions, "
                   "from_pvk_db.Perovskite_composition_c_ions, device_attributes.Perovskite_composition_c_ions, "
                   "from_pvk_db.Perovskite_composition_a_ions_coefficients, device_attributes.Perovskite_composition_a_ions_coefficients, "
                   "from_pvk_db.Perovskite_composition_b_ions_coefficients, device_attributes.Perovskite_composition_b_ions_coefficients, "
                   "from_pvk_db.Perovskite_composition_c_ions_coefficients, device_attributes.Perovskite_composition_c_ions_coefficients "
                   "from from_pvk_db, device_attributes where from_pvk_db.Ref_DOI_number = device_attributes.Ref_DOI_number")
    Perovskite_ions= cursor.fetchall()
    y_testi = []
    y_predi = []
    y_testbi = []
    y_predbi = []
    y_testci = []
    y_predci = []
    y_test = []
    y_pred = []
    y_testb = []
    y_predb = []
    y_testc = []
    y_predc = []
    for row in Perovskite_ions:
        if '|' not in row['Perovskite_composition_a_ions_coefficients'] != '' and 'x' not in row['Perovskite_composition_a_ions_coefficients'] != ''\
                and 'x' not in row['Perovskite_composition_c_ions_coefficients'] != '' and row['device_attributes.Perovskite_composition_a_ions'] != '':
            pvk_db_a = dict(sorted(dict(zip(row['Perovskite_composition_a_ions'].split('; '), ['%.2f' % float(elem) for elem in row['Perovskite_composition_a_ions_coefficients'].split('; ')])).items()))
            pvk_db_Perovskite_composition_a_ions = pvk_db_a.keys()
            y_testi.append(str(sorted(pvk_db_Perovskite_composition_a_ions)))
            pvk_db_Perovskite_composition_a_ions_coefficients = ['%.2f' % float(elem) for elem in pvk_db_a.values()]
            y_test.append(str(sorted(pvk_db_Perovskite_composition_a_ions_coefficients)))
            mined_a = dict(sorted(dict(zip(row['device_attributes.Perovskite_composition_a_ions'].split(', '), ['%.2f' % float(elem) for elem in row['device_attributes.Perovskite_composition_a_ions_coefficients'].split(', ')])).items()))
            mined_Perovskite_composition_a_ions = mined_a.keys()
            y_predi.append(str(sorted(mined_Perovskite_composition_a_ions)))
            mined_Perovskite_composition_a_ions_coefficients = ['%.2f' % float(elem) for elem in mined_a.values()]
            y_pred.append(str(sorted(mined_Perovskite_composition_a_ions_coefficients)))

            pvk_db_b = dict(sorted(dict(zip(row['Perovskite_composition_b_ions'].split('; '), ['%.2f' % float(elem) for elem in row['Perovskite_composition_b_ions_coefficients'].split('; ')])).items()))
            pvk_db_Perovskite_composition_b_ions = pvk_db_b.keys()
            y_testbi.append(str(sorted(pvk_db_Perovskite_composition_b_ions)))
            pvk_db_Perovskite_composition_b_ions_coefficients = pvk_db_b.values()
            y_testb.append(str(sorted(pvk_db_Perovskite_composition_b_ions_coefficients)))
            mined_b = dict(sorted(dict(zip(row['device_attributes.Perovskite_composition_b_ions'].split(', '), ['%.2f' % float(elem) for elem in row['device_attributes.Perovskite_composition_b_ions_coefficients'].split(', ')])).items()))
            mined_Perovskite_composition_b_ions = mined_b.keys()
            y_predbi.append(str(sorted(mined_Perovskite_composition_b_ions)))
            mined_Perovskite_composition_b_ions_coefficients = mined_b.values()
            y_predb.append(str(sorted(mined_Perovskite_composition_b_ions_coefficients)))

            pvk_db_c = dict(sorted(dict(zip(row['Perovskite_composition_c_ions'].split('; '), ['%.2f' % float(elem) for elem in row['Perovskite_composition_c_ions_coefficients'].split('; ')])).items()))
            pvk_db_Perovskite_composition_c_ions = pvk_db_c.keys()
            y_testci.append(str(sorted(pvk_db_Perovskite_composition_c_ions)))
            pvk_db_Perovskite_composition_c_ions_coefficients = pvk_db_c.values()
            y_testc.append(str(sorted(pvk_db_Perovskite_composition_c_ions_coefficients)))
            mined_c = dict(sorted(dict(zip(row['device_attributes.Perovskite_composition_c_ions'].split(', '), ['%.2f' % float(elem) for elem in row['device_attributes.Perovskite_composition_c_ions_coefficients'].split(', ')])).items()))
            mined_Perovskite_composition_c_ions = mined_c.keys()
            y_predci.append(str(sorted(mined_Perovskite_composition_c_ions)))
            mined_Perovskite_composition_c_ions_coefficients = mined_c.values()
            y_predc.append(str(sorted(mined_Perovskite_composition_c_ions_coefficients)))

    print('IONS (A, B, X)')
    print('Accuracy:', accuracy_score(y_testi, y_predi))
    print('Precision (weighted, labels=np.unique(y_pred)):',
          precision_score(y_testi, y_predi, average='weighted', labels=np.unique(y_predi)))
    print('Recall (weighted):',
          recall_score(y_testi, y_predi, average='weighted', labels=np.unique(y_predi)))
    print('F1 score (weighted):',
          f1_score(y_testi, y_predi, average='weighted', labels=np.unique(y_predi)))
    print('Accuracy:', accuracy_score(y_testbi, y_predbi))
    print('Precision (weighted, labels=np.unique(y_pred)):',
          precision_score(y_testbi, y_predbi, average='weighted', labels=np.unique(y_predbi)))
    print('Recall (weighted):',
          recall_score(y_testbi, y_predbi, average='weighted', labels=np.unique(y_predbi)))
    print('F1 score (weighted):',
          f1_score(y_testbi, y_predbi, average='weighted', labels=np.unique(y_predbi)))
    print('Accuracy:', accuracy_score(y_testci, y_predci))
    print('Precision (weighted, labels=np.unique(y_pred)):',
          precision_score(y_testci, y_predci, average='weighted', labels=np.unique(y_predci)))
    print('Recall (weighted):',
          recall_score(y_testci, y_predci, average='weighted', labels=np.unique(y_predci)))
    print('F1 score (weighted):',
          f1_score(y_testci, y_predci, average='weighted', labels=np.unique(y_predci)))
    print('--------------------------------------------------')
    print('COEFFICIENT (A, B, X)')
    print('Accuracy:', accuracy_score(y_test, y_pred))
    print('Accuracy:', accuracy_score(y_testb, y_predb))
    print('Accuracy:', accuracy_score(y_testc, y_predc))
    print('--------------------------------------------------')

def eval_top_contact():
    cursor.execute("select from_pvk_db.Ref_DOI_number, from_pvk_db.Backcontact_stack_sequence, "
                   "from_pvk_db.Backcontact_thickness_list, from_pvk_db.Backcontact_deposition_procedure, "
                   "device_attributes.Top_contact, device_attributes.Top_contact_thickness, "
                   "device_attributes.Top_contact_deposition from from_pvk_db, device_attributes "
                   "where from_pvk_db.Ref_DOI_number = device_attributes.Ref_DOI_number")
    Top_contact_result = cursor.fetchall()
    y_test = []
    y_pred = []
    y_test_procedure = []
    y_pred_procedure = []
    thickness_correct = 0
    thickness_within_range = 0
    thickness_wrong = 0
    count_one = 0
    count_none = 0
    count_one_thickness = 0
    count_none_thickness = 0
    count_one_procedure = 0
    count_none_procedure = 0
    for row in Top_contact_result:
        pvk_db_Top_contact = row['Backcontact_stack_sequence']
        mined_Top_contact = row['Top_contact']
        if ' | ' in pvk_db_Top_contact:
            pvk_db_Top_contact = pvk_db_Top_contact.split(' | ')[-1]
        if mined_Top_contact == 'carbon':
            mined_Top_contact = 'Carbon'
        if 'Carbon' in pvk_db_Top_contact:
            pvk_db_Top_contact = 'Carbon'
        if pvk_db_Top_contact != '' and mined_Top_contact != '':
            y_test.append(pvk_db_Top_contact)
            y_pred.append(mined_Top_contact)
            count_one += 1
        else:
            count_none += 1
        pvk_db_Top_contact_procedure = row['Backcontact_deposition_procedure']
        mined_Top_contact_procedure = row['Top_contact_deposition']
        if ' | ' in pvk_db_Top_contact_procedure:
            pvk_db_Top_contact_procedure = pvk_db_Top_contact_procedure.split(' | ')[-1]
        if pvk_db_Top_contact_procedure == 'Magnetron sputtering':
            pvk_db_Top_contact_procedure = 'Sputtering'
        if pvk_db_Top_contact_procedure != '' and mined_Top_contact_procedure != '':
            y_test_procedure.append(pvk_db_Top_contact_procedure.lower())
            y_pred_procedure.append(mined_Top_contact_procedure.lower())
            count_one_procedure += 1
        else:
            count_none_procedure += 1
        pvk_db_Top_contact_thickness = row['Backcontact_thickness_list']
        mined_Top_contact_thickness = row['Top_contact_thickness']
        if pvk_db_Top_contact_thickness != '' and pvk_db_Top_contact_thickness != 'nan' \
                and mined_Top_contact_thickness != '':
            if ' | ' in pvk_db_Top_contact_thickness:
                pvk_db_Top_contact_thickness = pvk_db_Top_contact_thickness.split(' | ')[-1]
            try:
                if '-' in mined_Top_contact_thickness:
                    range_start = float(mined_Top_contact_thickness[:-3].split('-')[0])
                    range_end = float(mined_Top_contact_thickness[:-3].split('-')[1])
                    if float(pvk_db_Top_contact_thickness) >= range_start and float(pvk_db_Top_contact_thickness) <= range_end:
                        thickness_correct += 1
                        thickness_within_range += 1
                    else:
                        thickness_wrong += 1
                elif '-' not in mined_Top_contact_thickness:
                    if float(pvk_db_Top_contact_thickness) == float(mined_Top_contact_thickness[:-3]):
                        thickness_correct += 1
                    else:
                        thickness_wrong += 1
            except:
                print(pvk_db_Top_contact_thickness, end=' ')
                print(mined_Top_contact_thickness)
            count_one_thickness += 1
        else:
            count_none_thickness += 1
    print('TOP CONTACT MATERIAL (CLASSIFIER):')
    print('Accuracy:', accuracy_score(y_test, y_pred))
    print('Precision (weighted, labels=np.unique(y_pred)):',
          precision_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('Recall (weighted):',
          recall_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('F1 score (weighted):',
          f1_score(y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    print('not none:' + str(count_one))
    print('none:' + str(count_none))
    print('--------------------------------------------------')
    print('TOP CONTACT DEPOSITION PROCEDURE (CLASSIFIER):')
    print('Accuracy:', accuracy_score(y_test_procedure, y_pred_procedure))
    print('Precision (weighted, labels=np.unique(y_pred)):',
          precision_score(y_test_procedure, y_pred_procedure, average='weighted', labels=np.unique(y_pred_procedure)))
    print('Recall (weighted):',
          recall_score(y_test_procedure, y_pred_procedure, average='weighted', labels=np.unique(y_pred_procedure)))
    print('F1 score (weighted):',
          f1_score(y_test_procedure, y_pred_procedure, average='weighted', labels=np.unique(y_pred_procedure)))
    print('not none:' + str(count_one_procedure))
    print('none:' + str(count_none_procedure))
    print('--------------------------------------------------')
    print('THICKNESS (PREDICTOR):')
    print('Accuracy:', thickness_correct/(thickness_wrong + thickness_correct))
    print('Thickness within range:', thickness_within_range)
    print('Thickness exactly correct:', thickness_correct - thickness_within_range)
    print('Thickness wrong:', thickness_wrong)
    print('Thickness NAN:', str(count_none_thickness))
    print('--------------------------------------------------')

def eval_HTL_procedure_parameters():
    cursor.execute("select from_pvk_db.Ref_DOI_number, from_pvk_db.HTL, "
                   "from_pvk_db.HTL_deposition_procedure, device_attributes.HTL, "
                   "device_attributes.HTL_deposition from from_pvk_db, device_attributes "
                   "where from_pvk_db.Ref_DOI_number = device_attributes.Ref_DOI_number")
    HTL_result = cursor.fetchall()
    y_test_procedure = []
    y_pred_procedure = []
    count_one_procedure = 0
    count_none_procedure = 0
    for row in HTL_result:
        pvk_db_procedure = row['HTL_deposition_procedure']
        mined_procedure = row['HTL_deposition']
        if ' | ' in pvk_db_procedure:
            pvk_db_procedure = pvk_db_procedure.split(' | ')[0]
        if pvk_db_procedure != '' and mined_procedure != '':
            if 'spray' in pvk_db_procedure.lower():
                pvk_db_procedure = 'Spray pyrolysis'
            if pvk_db_procedure == 'Dipp-coating':
                pvk_db_procedure = 'Dip-coating'
            y_test_procedure.append(pvk_db_procedure.lower())
            y_pred_procedure.append(mined_procedure.lower())
            count_one_procedure += 1
        else:
            count_none_procedure += 1
    print('HTL DEPOSITION PROCEDURE (CLASSIFIER):')
    print('Accuracy:', accuracy_score(y_test_procedure, y_pred_procedure))
    print('Precision (weighted, labels=np.unique(y_pred)):',
          precision_score(y_test_procedure, y_pred_procedure, average='weighted', labels=np.unique(y_pred_procedure)))
    print('Recall (weighted):',
          recall_score(y_test_procedure, y_pred_procedure, average='weighted', labels=np.unique(y_pred_procedure)))
    print('F1 score (weighted):',
          f1_score(y_test_procedure, y_pred_procedure, average='weighted', labels=np.unique(y_pred_procedure)))
    print('not none:' + str(count_one_procedure))
    print('none:' + str(count_none_procedure))
    print('--------------------------------------------------')

def eval_PVK_procedure_parameters():
    cursor.execute("select from_pvk_db.Ref_DOI_number, "
                   "from_pvk_db.Perovskite_deposition_procedure, "
                   "device_attributes.Perovskite_deposition from from_pvk_db, device_attributes "
                   "where from_pvk_db.Ref_DOI_number = device_attributes.Ref_DOI_number")
    HTL_result = cursor.fetchall()
    y_test_procedure = []
    y_pred_procedure = []
    count_one_procedure = 0
    count_none_procedure = 0
    for row in HTL_result:
        pvk_db_procedure = row['Perovskite_deposition_procedure']
        mined_procedure = row['Perovskite_deposition']
        if ' >> ' in pvk_db_procedure:
            # print(pvk_db_procedure.split(' >> '))
            pvk_db_procedure = pvk_db_procedure.split(' >> ')[0]
        if pvk_db_procedure != '' and mined_procedure != '':
            if 'evaporation' in pvk_db_procedure:
                pvk_db_procedure = 'evaporation'
            y_test_procedure.append(pvk_db_procedure.lower())
            y_pred_procedure.append(mined_procedure.lower())
            count_one_procedure += 1
        else:
            count_none_procedure += 1
    print('PEROVSKITE DEPOSITION PROCEDURE (CLASSIFIER):')
    print('Accuracy:', accuracy_score(y_test_procedure, y_pred_procedure))
    print('Precision (weighted, labels=np.unique(y_pred)):',
          precision_score(y_test_procedure, y_pred_procedure, average='weighted', labels=np.unique(y_pred_procedure)))
    print('Recall (weighted):',
          recall_score(y_test_procedure, y_pred_procedure, average='weighted', labels=np.unique(y_pred_procedure)))
    print('F1 score (weighted):',
          f1_score(y_test_procedure, y_pred_procedure, average='weighted', labels=np.unique(y_pred_procedure)))
    print('not none:' + str(count_one_procedure))
    print('none:' + str(count_none_procedure))
    print('--------------------------------------------------')

def eval_ETL_procedure_parameters():
    cursor.execute("select from_pvk_db.Ref_DOI_number, from_pvk_db.ETL, "
                   "from_pvk_db.ETL_deposition_procedure, device_attributes.ETL, "
                   "device_attributes.ETL_deposition from from_pvk_db, device_attributes "
                   "where from_pvk_db.Ref_DOI_number = device_attributes.Ref_DOI_number")
    ETL_result = cursor.fetchall()
    y_test_procedure = []
    y_pred_procedure = []
    count_one_procedure = 0
    count_none_procedure = 0
    for row in ETL_result:
        pvk_db_procedure = row['ETL_deposition_procedure']
        mined_procedure = row['ETL_deposition']
        if ' | ' in pvk_db_procedure:
            temp_pvk_db_procedure = pvk_db_procedure.split(' | ')[0]
            if temp_pvk_db_procedure == 'Spray-pyrolys':
                pvk_db_procedure = pvk_db_procedure.split(' | ')[1]
            else:
                pvk_db_procedure = pvk_db_procedure.split(' | ')[0]
        if pvk_db_procedure != '' and mined_procedure != '':
            if 'spray' in pvk_db_procedure.lower():
                pvk_db_procedure = 'Spray pyrolysis'
            if pvk_db_procedure == 'Dipp-coating':
                pvk_db_procedure = 'Dip-coating'
            y_test_procedure.append(pvk_db_procedure.lower())
            y_pred_procedure.append(mined_procedure.lower())
            count_one_procedure += 1
        else:
            count_none_procedure += 1
    print('ETL DEPOSITION PROCEDURE (CLASSIFIER):')
    print('Accuracy:', accuracy_score(y_test_procedure, y_pred_procedure))
    print('Precision (weighted, labels=np.unique(y_pred)):',
          precision_score(y_test_procedure, y_pred_procedure, average='weighted', labels=np.unique(y_pred_procedure)))
    print('Recall (weighted):',
          recall_score(y_test_procedure, y_pred_procedure, average='weighted', labels=np.unique(y_pred_procedure)))
    print('F1 score (weighted):',
          f1_score(y_test_procedure, y_pred_procedure, average='weighted', labels=np.unique(y_pred_procedure)))
    print('not none:' + str(count_one_procedure))
    print('none:' + str(count_none_procedure))
    print('--------------------------------------------------')

def eval_pvk_anneal():
    cursor.execute("select from_pvk_db.Ref_DOI_number, from_pvk_db.Perovskite_deposition_thermal_annealing_time, "
                   "from_pvk_db.Perovskite_deposition_thermal_annealing_temperature, device_attributes.Perovskite_annealing_parameters "
                   "from from_pvk_db, device_attributes "
                   "where from_pvk_db.Ref_DOI_number = device_attributes.Ref_DOI_number")
    ann_result = cursor.fetchall()
    count_correct = 0
    count_wrong = 0
    count_one_procedure = 0
    count_none_procedure = 0
    anneal_temperature = 0
    anneal_duration = 0
    anneal_temperature_1 = 0
    anneal_duration_1 = 0
    mined_anneal_temperature = 0
    mined_anneal_duration = 0
    pvk_db_procedure_1 = ''
    pvk_db_procedure2_1 = ''
    for row in ann_result:
        pvk_db_procedure = row['Perovskite_deposition_thermal_annealing_temperature']
        pvk_db_procedure2 = row['Perovskite_deposition_thermal_annealing_time']
        mined_procedure = row['Perovskite_annealing_parameters']
        if ' >> ' in pvk_db_procedure and ' >> ' in pvk_db_procedure2:
            pvk_db_procedure_1 = pvk_db_procedure.split(' >> ')[-1]
            pvk_db_procedure2_1 = pvk_db_procedure2.split(' >> ')[-1]
            pvk_db_procedure = pvk_db_procedure.split(' >> ')[0]
            pvk_db_procedure2 = pvk_db_procedure2.split(' >> ')[0]
        if '; ' in pvk_db_procedure and '; ' in pvk_db_procedure2:
            pvk_db_procedure_1 = pvk_db_procedure.split('; ')[-1]
            pvk_db_procedure2_1 = pvk_db_procedure2.split('; ')[-1]
            pvk_db_procedure = pvk_db_procedure.split('; ')[0]
            pvk_db_procedure2 = pvk_db_procedure2.split('; ')[0]
        if 'Unknown' in pvk_db_procedure or 'Unknown' in pvk_db_procedure2\
                or ' >> ' in pvk_db_procedure or ' >> ' in pvk_db_procedure2\
                or '; ' in pvk_db_procedure or '; ' in pvk_db_procedure2\
                or mined_procedure == '':
            count_none_procedure += 1
        else:
            try:
                anneal_temperature = float(pvk_db_procedure)
                anneal_duration = float(pvk_db_procedure2)
                if pvk_db_procedure_1 != '' and pvk_db_procedure2_1 != '' and 'Unknown' not in pvk_db_procedure_1 and 'Unknown' not in pvk_db_procedure2_1:
                    anneal_temperature_1 = float(pvk_db_procedure_1)
                    anneal_duration_1 = float(pvk_db_procedure2_1)
                mined_anneal_temperature = float(mined_procedure.split(' C ')[0])
                mined_anneal_duration = mined_procedure.split(' C ')[1]
                if ' min' in mined_anneal_duration:
                    mined_anneal_duration = float(mined_anneal_duration.split(' min')[0])
                elif ' h' in mined_anneal_duration:
                    mined_anneal_duration = float(mined_anneal_duration.split(' h')[0]) * 60
                count_one_procedure += 1
            except:
                print('not float')

            if anneal_temperature == mined_anneal_temperature and anneal_duration == mined_anneal_duration:
                count_correct += 1
            elif anneal_temperature_1 == mined_anneal_temperature and anneal_duration_1 == mined_anneal_duration:
                count_correct += 1
            else:
                count_wrong += 1
    print('PVK ANNEALING PARAMETERS (PREDICTOR):')
    print('Accuracy:' + str(count_correct / (count_wrong + count_correct)))
    print('correct:' + str(count_correct))
    print('wrong:' + str(count_wrong))
    print('not none:' + str(count_one_procedure))
    print('none:' + str(count_none_procedure))
    print('--------------------------------------------------')

def eval_manual():
    cursor.execute("select HTL_spin_wrong, HTL_ann_wrong, PVK_spin_wrong "
                   "from device_attributes_manual")
    ann_result = cursor.fetchall()
    count_correct = 0
    count_wrong = 0
    count_correct2 = 0
    count_wrong2 = 0
    count_correct3 = 0
    count_wrong3 = 0
    for row in ann_result:
        procedure = row['HTL_spin_wrong']
        procedure2 = row['HTL_ann_wrong']
        procedure3 = row['PVK_spin_wrong']
        if procedure == 'c':
            count_correct += 1
        elif procedure == 'w':
            count_wrong += 1
        if procedure2 == 'c':
            count_correct2 += 1
        elif procedure2 == 'w':
            count_wrong2 += 1
        if procedure3 == 'c':
            count_correct3 += 1
        elif procedure3 == 'w':
            count_wrong3 += 1
    print('MANUAL - HTL spin coating:')
    print('Accuracy:' + str(count_correct / (count_wrong + count_correct)))
    print('--------------------------------------------------')
    print('MANUAL - HTL annealing:')
    print('Accuracy:' + str(count_correct2 / (count_wrong2 + count_correct2)))
    print('--------------------------------------------------')
    print('MANUAL - PVK spin coating:')
    print('Accuracy:' + str(count_correct3 / (count_wrong3 + count_correct3)))
    print('--------------------------------------------------')

def eval_manual_etl():
    cursor.execute("select ETL_spin_wrong, ETL_ann_wrong "
                   "from device_attributes_manual_etl")
    ann_result = cursor.fetchall()
    count_correct = 0
    count_wrong = 0
    count_correct2 = 0
    count_wrong2 = 0
    for row in ann_result:
        procedure = row['ETL_spin_wrong']
        procedure2 = row['ETL_ann_wrong']
        if procedure == 'c':
            count_correct += 1
        elif procedure == 'w':
            count_wrong += 1
        if procedure2 == 'c':
            count_correct2 += 1
        elif procedure2 == 'w':
            count_wrong2 += 1
    print('MANUAL - ETL spin coating:')
    print('Accuracy:' + str(count_correct / (count_wrong + count_correct)))
    print('--------------------------------------------------')
    print('MANUAL - ETL annealing:')
    print('Accuracy:' + str(count_correct2 / (count_wrong2 + count_correct2)))
    print('--------------------------------------------------')

eval_substrate()
eval_flexible()
eval_architecture()
eval_ETL()
eval_HTL()
eval_pvk_short_form()
eval_pvk_long_form()
eval_pvk_ions()
eval_top_contact()
eval_HTL_procedure_parameters()
eval_PVK_procedure_parameters()
eval_ETL_procedure_parameters()
eval_pvk_anneal()
eval_manual()
eval_manual_etl()