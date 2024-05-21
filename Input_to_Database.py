# coding:utf-8
import pymysql
import os
from bs4 import BeautifulSoup
from chemdataextractor.doc import Paragraph
from f import substrate_mining, perovskite_composition_mining, perovskite_ratio, cell_architecture_mining, \
    HTL_mining, ETL_mining, deposition_method_mining

folder = 'htmls'     # contains the htmls, txts, and pdfs from which data is mined

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

def get_htmls():
    html_files = []
    for (root, dirs, files) in os.walk('.', topdown=True):
        if folder in root:
            for file in files:
                if '.html' in file:
                    html_files.append(folder + '/' + file)
    return html_files

def get_txts():
    txt_files = []
    for (root, dirs, files) in os.walk('.', topdown=True):
        if folder in root:
            for file in files:
                if '.txt' in file:
                    txt_files.append(file)
    return txt_files

def data_insert_ref(html_files):
    for f in html_files:
        try:
            if '10.1038' in f:      # Nature
                cont = open(f, "r", encoding="utf-8")
                soup = BeautifulSoup(cont, "lxml")
                html_link = soup.find("meta", attrs={'name': "citation_fulltext_html_url"})["content"]
                title = soup.find("meta", attrs={'name': "citation_title"})["content"]
                doi = soup.find("meta", attrs={'name': "DOI"})["content"]
                publication_date = soup.find("meta", attrs={'name': "dc.date"})["content"]
                author = soup.find("meta", attrs={'name': "dc.creator"})["content"]
                sqlStr = "insert into device_attributes(`Ref_DOI_number`,`Ref_lead_author`,`Ref_publication_date`,`Ref_title`,`Ref_html_link`)" \
                         "VALUES ('%s','%s','%s','%s','%s');" \
                            % (doi, author, publication_date, title, html_link)
                res = cursor.execute(sqlStr)
                conn.commit()
            elif '10.1039' in f:    # RSC
                cont = open(f, "r", encoding="utf-8")
                soup = BeautifulSoup(cont, "lxml")
                html_link = soup.find("meta", attrs={'name': "citation_fulltext_html_url"})["content"]
                title = soup.find("meta", attrs={'name': "citation_title"})["content"]
                doi = soup.find("meta", attrs={'name': "citation_doi"})["content"]
                publication_date = soup.find("meta", attrs={'name': "citation_online_date"})["content"]
                author = soup.find("meta", attrs={'name': "DC.Creator"})["content"]
                sqlStr = "insert into device_attributes(`Ref_DOI_number`,`Ref_lead_author`,`Ref_publication_date`,`Ref_title`,`Ref_html_link`)" \
                         "VALUES ('%s','%s','%s','%s','%s');" \
                            % (doi, author, publication_date, title, html_link)
                res = cursor.execute(sqlStr)
                conn.commit()
        except:
            print('duplicate', end=' ')

def data_insert_substrate(txt_files):
    for fil in txt_files:
        method_list = []
        with open(folder + '/' + fil, 'r', encoding='utf8') as f:
            while True:
                section_number = f.readline().rstrip('\n')
                tex = f.readline().rstrip('\n')
                if not section_number or not tex:
                    break  # EOF
                method_list.append([section_number, tex])
        substrate_sen_all = []
        flexible_final = 'FALSE'
        if '10.1038' in fil:
            for process in method_list:
                if 'content' in process[0]:
                    para = Paragraph(process[1])
                    substrate_sen, flex_sen = substrate_mining(para)
                    substrate_sen_all.append(substrate_sen)
                    if flex_sen == 1:
                        flexible_final = 'TRUE'
        elif '10.1039' in fil:
            for process in method_list:
                para = Paragraph(process[1])
                substrate_sen, flex_sen = substrate_mining(para)
                substrate_sen_all.append(substrate_sen)
                if flex_sen == 1:
                    flexible_final = 'TRUE'
        substrate_final = ''
        substrate_count = {'FTO': 0, 'ITO': 0, 'PEN': 0, 'PET': 0}
        for lis in substrate_sen_all:
            for v in lis:
                substrate_count[v] += 1
        if substrate_count['PEN'] > substrate_count['PET']:
            substrate_final = 'PEN'
        elif substrate_count['PEN'] < substrate_count['PET']:
            substrate_final = 'PET'
        else:
            substrate_final = 'SLG'
        if substrate_count['ITO'] != substrate_count['FTO']:
            substrate_final += ' | '
        if substrate_count['FTO'] > substrate_count['ITO']:
            substrate_final += 'FTO'
        elif substrate_count['FTO'] < substrate_count['ITO']:
            substrate_final += 'ITO'
        if substrate_final == 'SLG':
            substrate_final = 'UNKNOWN'
        sqlStr = "update device_attributes set `Substrate` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (substrate_final, fil[0:7]+'/'+fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
        res = cursor.execute(sqlStr)
        sqlStr2 = "update device_attributes set `Cell_flexible` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (flexible_final, fil[0:7]+'/'+fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
        res2 = cursor.execute(sqlStr2)
        conn.commit()

def data_insert_HTL(txt_files, HTLs, HTLs_mult):
    for fil in txt_files:
        method_list = []
        bo = 1
        HTL_final = 'UNKNOWN'
        HTL_count = {}
        if '10.1038' in fil:
            with open(folder + '/' + fil, 'r', encoding='utf8') as f:
                while True:
                    section_number = f.readline().rstrip('\n')
                    tex = f.readline().rstrip('\n')
                    if not section_number or not tex:
                        break  # EOF
                    if ('Method' in tex or 'Experimental' in tex or 'fabrication' in tex) and 'content' not in section_number:
                        bo = 1
                    if tex in ['Additional information', 'Supplementary information', 'Data availability'] \
                            and 'content' not in section_number:
                        break
                    if bo == 1:
                        method_list.append([section_number, tex])
            for process in method_list:
                if 'content' in process[0]:
                    para = Paragraph(process[1])
                    HTL_sen = HTL_mining(para, HTLs, HTLs_mult)
                    if HTL_sen != []:
                        for ht in HTL_sen:
                            if ht in HTL_count:
                                HTL_count[ht] += 1
                            else:
                                HTL_count[ht] = 1
        elif '10.1039' in fil:
            with open(folder + '/' + fil, 'r', encoding='utf8') as f:
                while True:
                    section_number = f.readline().rstrip('\n')
                    tex = f.readline().rstrip('\n')
                    if not section_number or not tex:
                        break  # EOF
                    if 'Method' in tex or 'Experimental' in tex or 'fabrication' in tex:
                        bo = 1
                    if tex in ['Additional information', 'Supplementary information', 'Data availability']:
                        break
                    if bo == 1:
                        method_list.append([section_number, tex])
            for process in method_list:
                para = Paragraph(process[1])
                HTL_sen = HTL_mining(para, HTLs, HTLs_mult)
                if HTL_sen != []:
                    for ht in HTL_sen:
                        if ht in HTL_count:
                            HTL_count[ht] += 1
                        else:
                            HTL_count[ht] = 1
        sorted_HTL = sorted(HTL_count.items(), key=lambda x: x[1], reverse=True)
        for first in sorted_HTL:
            HTL_final = first[0]
            break
        sqlStr = "update device_attributes set `HTL` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (HTL_final, fil[0:7]+'/'+fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
        res = cursor.execute(sqlStr)
        conn.commit()

def data_insert_ETL(txt_files, ETLs, ETLs_mult):
    for fil in txt_files:
        method_list = []
        bo = 1
        ETL_final = 'UNKNOWN'
        ETL_count = {}
        if '10.1038' in fil:
            with open(folder + '/' + fil, 'r', encoding='utf8') as f:
                while True:
                    section_number = f.readline().rstrip('\n')
                    tex = f.readline().rstrip('\n')
                    if not section_number or not tex:
                        break  # EOF
                    if ('Method' in tex or 'Experimental' in tex or 'fabrication' in tex) and 'content' not in section_number:
                        bo = 1
                    if tex in ['Additional information', 'Supplementary information', 'Data availability'] \
                            and 'content' not in section_number:
                        break
                    if bo == 1:
                        method_list.append([section_number, tex])
            for process in method_list:
                if 'content' in process[0]:
                    para = Paragraph(process[1])
                    ETL_sen = ETL_mining(para, ETLs, ETLs_mult)      # HTLs.index(word) for priority
                    if ETL_sen != []:
                        for et in ETL_sen:
                            if et in ETL_count:
                                ETL_count[et] += 1
                            else:
                                ETL_count[et] = 1
        elif '10.1039' in fil:
            with open(folder + '/' + fil, 'r', encoding='utf8') as f:
                while True:
                    section_number = f.readline().rstrip('\n')
                    tex = f.readline().rstrip('\n')
                    if not section_number or not tex:
                        break  # EOF
                    if 'Method' in tex or 'Experimental' in tex or 'fabrication' in tex:
                        bo = 1
                    if tex in ['Additional information', 'Supplementary information', 'Data availability'] \
                            and 'content' not in section_number:
                        break
                    if bo == 1:
                        method_list.append([section_number, tex])
            for process in method_list:
                para = Paragraph(process[1])
                ETL_sen = ETL_mining(para, ETLs, ETLs_mult)      # ETLs.index(word) for priority
                if ETL_sen != []:
                    for et in ETL_sen:
                        if et in ETL_count:
                            ETL_count[et] += 1
                        else:
                            ETL_count[et] = 1
        sorted_ETL = sorted(ETL_count.items(), key=lambda x: x[1], reverse=True)
        for first in sorted_ETL:
            ETL_final = first[0]
            break
        sqlStr = "update device_attributes set `ETL` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (ETL_final, fil[0:7]+'/'+fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
        res = cursor.execute(sqlStr)
        conn.commit()

def data_insert_cell_architecture(txt_files):
    for fil in txt_files:
        query = "select Ref_DOI_number, HTL from device_attributes where Ref_DOI_number = '%s' or Ref_html_link = '%s';"\
                % (fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/' + fil[8:-4])
        cursor.execute(query)
        HTL_result = cursor.fetchall()
        for row in HTL_result:
            DOI = row['Ref_DOI_number']
            HTL = row['HTL'].lower()
        materials = {'HTL': HTL}
        cell_architecture = ''
        method_list = []
        excess_part_method_list = []
        bo = 0
        # try:
        if '10.1038' in fil:
            with open(folder + '/' + fil, 'r', encoding='utf8') as f:
                while True:
                    section_number = f.readline().rstrip('\n')
                    tex = f.readline().rstrip('\n')
                    if not section_number or not tex:
                        break  # EOF
                    if ('method' in tex.lower() or 'experimental' in tex.lower() or 'fabrication' in tex.lower()) and 'content' not in section_number:
                        bo = 1
                    if bo == 1 and ('Results' in tex or 'Discussion' in tex) and 'content' not in section_number:
                        bo = 0
                    if bo == 1 and ('Results' in tex or 'Discussion' in tex or 'additional information' in tex.lower()
                                    or 'supplementary information' in tex.lower() or 'data availability' in tex.lower()) and 'content' not in section_number:
                        break
                    if bo == 1:
                        method_list.append([section_number, tex])
                    else:
                        excess_part_method_list.append([section_number, tex])

            for process in method_list:
                if 'content' in process[0]:
                    para = Paragraph(process[1])
                    cell_arc = cell_architecture_mining(para, materials)
                    if cell_arc == 1:
                        cell_architecture = 'nip'
                    elif cell_arc == 2:
                        cell_architecture = 'pin'
        elif '10.1039' in fil:
            with open(folder + '/' + fil, 'r', encoding='utf8') as f:
                while True:
                    section_number = f.readline().rstrip('\n')
                    tex = f.readline().rstrip('\n')
                    if not section_number or not tex:
                        break  # EOF
                    if 'from_pdf:' in section_number:
                        bo = 1
                    if ('method' in tex.lower() or 'experimental' in tex.lower() or 'fabrication' in tex.lower()):
                        if len(tex.lower()) < 50:
                            bo = 1
                    if ('Results' in tex or 'Discussion' in tex or 'additional information' in tex.lower()
                            or 'supplementary information' in tex.lower() or 'data availability' in tex.lower())\
                            and bo == 1:
                        break
                    if bo == 1:
                        method_list.append([section_number, tex])
                    else:
                        excess_part_method_list.append([section_number, tex])
            for process in method_list:
                para = Paragraph(process[1])
                cell_arc = cell_architecture_mining(para, materials)
                if cell_arc == 1:
                    cell_architecture = 'nip'
                elif cell_arc == 2:
                    cell_architecture = 'pin'
        sqlStr = "update device_attributes set `Cell_architecture` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (cell_architecture, fil[0:7]+'/'+fil[8:-4], 'https://www.nature.com/articles/' + fil[8:-4])
        res = cursor.execute(sqlStr)
        conn.commit()

def data_insert_perovskite_composition(txt_files):
    for fil in txt_files:
        method_list = []
        with open(folder + '/' + fil, 'r', encoding='utf8') as f:
            while True:
                section_number = f.readline().rstrip('\n')
                tex = f.readline().rstrip('\n')
                if not section_number or not tex:
                    break  # EOF
                method_list.append([section_number, tex])
        perovskite_composition_final = 'UNKNOWN'
        ABX_final = [[], [], []]
        ABX_ratio_final = [[], [], []]
        short_form = ''
        composition_count = {}
        if '10.1038' in fil:
            for process in method_list:
                if 'content' in process[0]:
                    para = Paragraph(process[1])
                    perovskite_composition_sen = perovskite_composition_mining(para)
                    if perovskite_composition_sen != '':
                        if perovskite_composition_sen in composition_count:
                            composition_count[perovskite_composition_sen] += 1
                        else:
                            composition_count[perovskite_composition_sen] = 1
        elif '10.1039' in fil:
            for process in method_list:
                para = Paragraph(process[1])
                perovskite_composition_sen = perovskite_composition_mining(para)
                if perovskite_composition_sen != '':
                    if perovskite_composition_sen in composition_count:
                        composition_count[perovskite_composition_sen] += 1
                    else:
                        composition_count[perovskite_composition_sen] = 1
        sorted_comp = sorted(composition_count.items(), key=lambda x:x[1], reverse=True)
        for first in sorted_comp:
            perovskite_composition_final = first[0]
            ABX_final, ABX_ratio_final, short_form, long_form_modified = perovskite_ratio(perovskite_composition_final)
            break
        try:
            sqlStr0 = "update device_attributes set `Perovskite_composition` = '%s'" \
                     "where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                     % (perovskite_composition_final, fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
            sqlStr1 = "update device_attributes set `Perovskite_composition_a_ions` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                     % (str(ABX_final[0]).replace("'", "").replace("[", "").replace("]", ""), fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
            sqlStr2 = "update device_attributes set `Perovskite_composition_b_ions` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                      % (str(ABX_final[1]).replace("'", "").replace("[", "").replace("]", ""), fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
            sqlStr3 = "update device_attributes set `Perovskite_composition_c_ions` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                      % (str(ABX_final[2]).replace("'", "").replace("[", "").replace("]", ""), fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
            sqlStr1c = "update device_attributes set `Perovskite_composition_a_ions_coefficients` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                     % (str(ABX_ratio_final[0]).replace("'", "").replace("[", "").replace("]", ""), fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
            sqlStr2c = "update device_attributes set `Perovskite_composition_b_ions_coefficients` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                      % (str(ABX_ratio_final[1]).replace("'", "").replace("[", "").replace("]", ""), fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
            sqlStr3c = "update device_attributes set `Perovskite_composition_c_ions_coefficients` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                      % (str(ABX_ratio_final[2]).replace("'", "").replace("[", "").replace("]", ""), fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
            sqlStrs = "update device_attributes set `Perovskite_composition_short_form` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                      % (short_form, fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
            res0 = cursor.execute(sqlStr0)
            res1 = cursor.execute(sqlStr1)
            res2 = cursor.execute(sqlStr2)
            res3 = cursor.execute(sqlStr3)
            res1c = cursor.execute(sqlStr1c)
            res2c = cursor.execute(sqlStr2c)
            res3c = cursor.execute(sqlStr3c)
            ress = cursor.execute(sqlStrs)
            conn.commit()
        except:
            print("exception")

def data_insert_deposition_method(txt_files):
    for fil in txt_files:
        try:
            query = "select Ref_DOI_number, ETL, HTL from device_attributes where Ref_DOI_number = '%s' or Ref_html_link = '%s';"\
                    % (fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/' + fil[8:-4])
            cursor.execute(query)
            ETL_result = cursor.fetchall()
            for row in ETL_result:
                DOI = row['Ref_DOI_number']
                ETL = row['ETL'].lower()
                HTL = row['HTL'].lower()
            materials = {'HTL': HTL, 'ETL': ETL}
            top_contact_material = ''
            top_contact_thickness = ''
            ETL_deposition = ''
            ETL_spin_coat_parameters = []
            ETL_anneal_parameters = []
            HTL_deposition = ''
            HTL_spin_coat_parameters = []
            HTL_anneal_parameters = []
            perovskite_deposition = ''
            perovskite_spin_coat_parameters = []
            perovskite_anneal_parameters = []
            Top_contact_deposition = ''
            method_list = []
            excess_part_method_list = []
            bo = 0
            try:
                if '10.1038' in fil:
                    with open(folder + '/' + fil, 'r', encoding='utf8') as f:
                        while True:
                            section_number = f.readline().rstrip('\n')
                            tex = f.readline().rstrip('\n')
                            if not section_number or not tex:
                                break  # EOF
                            if ('method' in tex.lower() or 'experimental' in tex.lower() or 'fabrication' in tex.lower()) and 'content' not in section_number:
                                bo = 1
                            if bo == 1 and ('Results' in tex or 'Discussion' in tex) and 'content' not in section_number:
                                bo = 0
                            if bo == 1 and ('Results' in tex or 'Discussion' in tex or 'additional information' in tex.lower()
                                            or 'supplementary information' in tex.lower() or 'data availability' in tex.lower()) and 'content' not in section_number:
                                break
                            if bo == 1:
                                method_list.append([section_number, tex])
                            else:
                                excess_part_method_list.append([section_number, tex])

                    for process in method_list:
                        if 'content' in process[0]:
                            para = Paragraph(process[1])
                            top_contact, thickness, dep_method, HTL_parameters, HTL_ann_parameters, \
                            pvk_parameters, pvk_ann_parameters, ETL_parameters, ETL_ann_parameters = deposition_method_mining(para, materials)
                            if top_contact_material == '' and top_contact != '':
                                top_contact_material = top_contact
                            if top_contact_thickness == '' and thickness != '':
                                top_contact_thickness = thickness
                            if Top_contact_deposition == '' and dep_method['top contact'] != '':
                                Top_contact_deposition = dep_method['top contact']
                            if ETL_deposition == '' and dep_method['ETL'] != '' and 'on it' not in dep_method['ETL']:
                                ETL_deposition = dep_method['ETL']
                            if ETL_spin_coat_parameters == [] and ETL_parameters != []:
                                ETL_spin_coat_parameters = ETL_parameters
                            if ETL_anneal_parameters == [] and ETL_ann_parameters != []:
                                ETL_anneal_parameters = ETL_ann_parameters
                            if HTL_deposition == '' and dep_method['HTL'] != '' and 'on it' not in dep_method['HTL']:
                                HTL_deposition = dep_method['HTL']
                            if HTL_spin_coat_parameters == [] and HTL_parameters != []:
                                HTL_spin_coat_parameters = HTL_parameters
                            if HTL_anneal_parameters == [] and HTL_ann_parameters != []:
                                HTL_anneal_parameters = HTL_ann_parameters
                            if perovskite_deposition == '' and dep_method['perovskite'] != '' and 'on it' not in dep_method['perovskite']:
                                perovskite_deposition = dep_method['perovskite']
                            if perovskite_spin_coat_parameters == [] and pvk_parameters != []:
                                perovskite_spin_coat_parameters = pvk_parameters
                            if perovskite_anneal_parameters == [] and pvk_ann_parameters != []:
                                perovskite_anneal_parameters = pvk_ann_parameters
                    if top_contact_material == '':
                        for process in excess_part_method_list:
                            if 'content' in process[0]:
                                para = Paragraph(process[1])
                                top_contact, thickness, dep_method, HTL_parameters, HTL_ann_parameters, \
                                pvk_parameters, pvk_ann_parameters, ETL_parameters, ETL_ann_parameters = deposition_method_mining(para, materials)
                                if top_contact_material == '' and top_contact != '':
                                    top_contact_material = top_contact
                                if top_contact_thickness == '' and thickness != '':
                                    top_contact_thickness = thickness
                                if Top_contact_deposition == '' and dep_method['top contact'] != '':
                                    Top_contact_deposition = dep_method['top contact']
                elif '10.1039' in fil:
                    with open(folder + '/' + fil, 'r', encoding='utf8') as f:
                        while True:
                            section_number = f.readline().rstrip('\n')
                            tex = f.readline().rstrip('\n')
                            if not section_number or not tex:
                                break  # EOF
                            if 'from_pdf:' in section_number:
                                bo = 1
                            if ('method' in tex.lower() or 'experimental' in tex.lower() or 'fabrication' in tex.lower()):
                                if len(tex.lower()) < 50:
                                    bo = 1
                            if ('Results' in tex or 'Discussion' in tex or 'additional information' in tex.lower()
                                    or 'supplementary information' in tex.lower() or 'data availability' in tex.lower())\
                                    and bo == 1:
                                break
                            if bo == 1:
                                method_list.append([section_number, tex])
                            else:
                                excess_part_method_list.append([section_number, tex])
                    for process in method_list:
                        para = Paragraph(process[1])
                        top_contact, thickness, dep_method, HTL_parameters, HTL_ann_parameters, \
                        pvk_parameters, pvk_ann_parameters, ETL_parameters, ETL_ann_parameters = deposition_method_mining(para, materials)
                        if top_contact_material == '' and top_contact != '':
                            top_contact_material = top_contact
                        if top_contact_thickness == '' and thickness != '':
                            top_contact_thickness = thickness
                        if Top_contact_deposition == '' and dep_method['top contact'] != '':
                            Top_contact_deposition = dep_method['top contact']
                        if ETL_deposition == '' and dep_method['ETL'] != '' and 'on it' not in dep_method['ETL']:
                            ETL_deposition = dep_method['ETL']
                        if ETL_spin_coat_parameters == [] and ETL_parameters != []:
                            ETL_spin_coat_parameters = ETL_parameters
                        if ETL_anneal_parameters == [] and ETL_ann_parameters != []:
                            ETL_anneal_parameters = ETL_ann_parameters
                        if HTL_deposition == '' and dep_method['HTL'] != '' and 'on it' not in dep_method['HTL']:
                            HTL_deposition = dep_method['HTL']
                        if HTL_spin_coat_parameters == [] and HTL_parameters != []:
                            HTL_spin_coat_parameters = HTL_parameters
                        if HTL_anneal_parameters == [] and HTL_ann_parameters != []:
                            HTL_anneal_parameters = HTL_ann_parameters
                        if perovskite_deposition == '' and dep_method['perovskite'] != '' and 'on it' not in dep_method['perovskite']:
                            perovskite_deposition = dep_method['perovskite']
                        if perovskite_spin_coat_parameters == [] and pvk_parameters != []:
                            perovskite_spin_coat_parameters = pvk_parameters
                        if perovskite_anneal_parameters == [] and pvk_ann_parameters != []:
                            perovskite_anneal_parameters = pvk_ann_parameters
                    if top_contact_material == '':
                        for process in excess_part_method_list:
                            para = Paragraph(process[1])
                            top_contact, thickness, dep_method, HTL_parameters, HTL_ann_parameters, \
                            pvk_parameters, pvk_ann_parameters, ETL_parameters, ETL_ann_parameters = deposition_method_mining(para, materials)
                            if top_contact_material == '' and top_contact != '':
                                top_contact_material = top_contact
                            if top_contact_thickness == '' and thickness != '':
                                top_contact_thickness = thickness
                            if Top_contact_deposition == '' and dep_method['top contact'] != '':
                                Top_contact_deposition = dep_method['top contact']
                sqlStr = "update device_attributes set `Top_contact` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                         % (top_contact_material, fil[0:7]+'/'+fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                sqlStrb = "update device_attributes set `Top_contact_thickness` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                         % (top_contact_thickness, fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                sqlStr1 = "update device_attributes set `ETL_deposition` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                          % (ETL_deposition, fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                sqlStr2 = "update device_attributes set `Perovskite_deposition` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                          % (perovskite_deposition, fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                sqlStr3 = "update device_attributes set `HTL_deposition` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                          % (HTL_deposition, fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                sqlStr4 = "update device_attributes set `Top_contact_deposition` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                          % (Top_contact_deposition, fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                res = cursor.execute(sqlStr)
                resb = cursor.execute(sqlStrb)
                res1 = cursor.execute(sqlStr1)
                res2 = cursor.execute(sqlStr2)
                res3 = cursor.execute(sqlStr3)
                res4 = cursor.execute(sqlStr4)
                if HTL_spin_coat_parameters != []:
                    if HTL_spin_coat_parameters[0][0] >= 10000 or HTL_spin_coat_parameters[0][0] < 100 \
                            or HTL_spin_coat_parameters[1][0] >= 1000:
                        lg_htl = ''
                    else:
                        lg_htl = str(str(HTL_spin_coat_parameters[0][0]) + " rpm " + str(HTL_spin_coat_parameters[1][0]) + " " + HTL_spin_coat_parameters[1][1])
                    sqlStr5a = "update device_attributes set `HTL_spin_coating_parameters` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                              % (lg_htl, fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                    res5a = cursor.execute(sqlStr5a)
                else:
                    sqlStr5a = "update device_attributes set `HTL_spin_coating_parameters` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                              % ('', fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                    res5a = cursor.execute(sqlStr5a)
                if HTL_anneal_parameters != []:
                    sqlStr6a = "update device_attributes set `HTL_annealing_parameters` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                              % (str(str(HTL_anneal_parameters[0][-1]) + " C " + str(HTL_anneal_parameters[1][0]) + " " + HTL_anneal_parameters[1][1]), fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                    res6a = cursor.execute(sqlStr6a)
                else:
                    sqlStr6a = "update device_attributes set `HTL_annealing_parameters` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                              % ('', fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                    res6a = cursor.execute(sqlStr6a)
                if ETL_spin_coat_parameters != []:
                    if ETL_spin_coat_parameters[0][0] >= 10000 or ETL_spin_coat_parameters[0][0] < 100 \
                            or ETL_spin_coat_parameters[1][0] >= 1000:
                        lg_etl = ''
                    else:
                        lg_etl = str(str(ETL_spin_coat_parameters[0][0]) + " rpm " + str(ETL_spin_coat_parameters[1][0]) + " " + ETL_spin_coat_parameters[1][1])
                    sqlStr5b = "update device_attributes set `ETL_spin_coating_parameters` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                              % (lg_etl, fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                    res5b = cursor.execute(sqlStr5b)
                else:
                    sqlStr5b = "update device_attributes set `ETL_spin_coating_parameters` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                              % ('', fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                    res5b = cursor.execute(sqlStr5b)
                if ETL_anneal_parameters != []:
                    sqlStr6b = "update device_attributes set `ETL_annealing_parameters` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                              % (str(str(ETL_anneal_parameters[0][-1]) + " C " + str(ETL_anneal_parameters[1][-2]) + " " + ETL_anneal_parameters[1][-1]), fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                    res6b = cursor.execute(sqlStr6b)
                else:
                    sqlStr6b = "update device_attributes set `ETL_annealing_parameters` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                              % ('', fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                    res6b = cursor.execute(sqlStr6b)
                if perovskite_spin_coat_parameters != []:
                    lg = ''
                    if len(perovskite_spin_coat_parameters[1]) == 2*len(perovskite_spin_coat_parameters[0]):
                        for x in range(len(perovskite_spin_coat_parameters[0])):
                            if perovskite_spin_coat_parameters[0][x] >= 10000 or perovskite_spin_coat_parameters[0][x] < 100 \
                                    or perovskite_spin_coat_parameters[1][2*x] >= 1000:
                                break
                            lg += (str(str(perovskite_spin_coat_parameters[0][x]) + " rpm " + str(
                            perovskite_spin_coat_parameters[1][2*x]) + " " + perovskite_spin_coat_parameters[1][2*x+1]) + " ")
                        lg = lg.rstrip()
                    else:
                        lg = str(str(perovskite_spin_coat_parameters[0][0]) + " rpm " + str(
                            perovskite_spin_coat_parameters[1][0]) + " " + perovskite_spin_coat_parameters[1][1])
                    sqlStr5 = "update device_attributes set `Perovskite_spin_coating_parameters` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                              % (lg, fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                    res5 = cursor.execute(sqlStr5)
                else:
                    sqlStr5 = "update device_attributes set `Perovskite_spin_coating_parameters` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                              % ('', fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                    res5 = cursor.execute(sqlStr5)
                if perovskite_anneal_parameters != []:
                    lg = ''
                    if len(perovskite_anneal_parameters[1]) == 2 * len(perovskite_anneal_parameters[0]):
                        for x in range(len(perovskite_anneal_parameters[0])):
                            lg += (str(str(perovskite_anneal_parameters[0][x]) + " C " + str(
                                perovskite_anneal_parameters[1][2 * x]) + " " + str(perovskite_anneal_parameters[1][2 * x + 1])) + " ")
                        lg = lg.rstrip()
                    else:
                        lg = str(str(perovskite_anneal_parameters[0][0]) + " C " + str(
                            perovskite_anneal_parameters[1][0]) + " " + perovskite_anneal_parameters[1][1])

                    sqlStr6 = "update device_attributes set `Perovskite_annealing_parameters` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                              % (lg, fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                    res6 = cursor.execute(sqlStr6)
                else:
                    sqlStr6 = "update device_attributes set `Perovskite_annealing_parameters` = '%s' where Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                              % ('', fil[0:7] + '/' + fil[8:-4], 'https://www.nature.com/articles/'+ fil[8:-4])
                    res6 = cursor.execute(sqlStr6)
                conn.commit()
            except:
                print('error: ', end=' ')
                print(fil)
        except:
            print('overall error: ', end=' ')
            print(fil)

def calculate_record_score():
    wanted_score = 0.7
    possible_wanted_score = 0.55
    total_score = 7
    try:
        query = "select * from device_attributes;"
        cursor.execute(query)
        record = cursor.fetchall()
        successful = 0
        unsuccessful = 0
        four_score = 0
        for row in record:
            try:
                record_score = 0
                DOI = row['Ref_DOI_number']
                if row['Substrate'] != 'UNKNOWN':
                    record_score += 1
                if row['Perovskite_composition_short_form'] != '':
                    record_score += 1
                if row['ETL'] != 'UNKNOWN':
                    record_score += 1
                if row['HTL'] != 'UNKNOWN':
                    record_score += 1
                if row['Top_contact'] != '':
                    record_score += 1
                if row['Perovskite_spin_coating_parameters'] != '':
                    record_score += 1
                if row['HTL_spin_coating_parameters'] != '':
                    record_score += 1
                if record_score/total_score >= wanted_score:
                    successful += 1
                    sqlStr = "insert ignore into device_attributes_filtered(`Ref_DOI_number`,`Ref_lead_author`,`Ref_publication_date`,`Ref_title`," \
                             "`Ref_html_link`,`Cell_architecture`,`Cell_flexible`,`Substrate`,`Perovskite_composition`,`Perovskite_composition_short_form`," \
                             "`Perovskite_composition_a_ions`,`Perovskite_composition_a_ions_coefficients`,`Perovskite_composition_b_ions`," \
                             "`Perovskite_composition_b_ions_coefficients`,`Perovskite_composition_c_ions`,`Perovskite_composition_c_ions_coefficients`" \
                             ",`ETL`,`Top_contact`,`Top_contact_thickness`,`Top_contact_deposition`,`HTL`,`HTL_deposition`,`HTL_spin_coating_parameters`," \
                             "`HTL_annealing_parameters`,`ETL_deposition`,`ETL_spin_coating_parameters`,`ETL_annealing_parameters`,`Perovskite_deposition`,`Perovskite_spin_coating_parameters`,`Perovskite_annealing_parameters`)" \
                             "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" \
                             % (row['Ref_DOI_number'], row['Ref_lead_author'], row['Ref_publication_date'], row['Ref_title'],
                                row['Ref_html_link'], row['Cell_architecture'], row['Cell_flexible'], row['Substrate'],
                                row['Perovskite_composition'], row['Perovskite_composition_short_form'], row['Perovskite_composition_a_ions'],
                                row['Perovskite_composition_a_ions_coefficients'], row['Perovskite_composition_b_ions'],
                                row['Perovskite_composition_b_ions_coefficients'], row['Perovskite_composition_c_ions'], row['Perovskite_composition_c_ions_coefficients'],
                                row['ETL'], row['Top_contact'], row['Top_contact_thickness'], row['Top_contact_deposition'],
                                row['HTL'], row['HTL_deposition'], row['HTL_spin_coating_parameters'], row['HTL_annealing_parameters'],
                                row['ETL_deposition'], row['ETL_spin_coating_parameters'], row['ETL_annealing_parameters'], row['Perovskite_deposition'],
                                row['Perovskite_spin_coating_parameters'], row['Perovskite_annealing_parameters'])
                    res = cursor.execute(sqlStr)
                    conn.commit()
                elif record_score/total_score >= possible_wanted_score:
                    four_score += 1
                else:
                    unsuccessful += 1
            except:
                print(row)
        print('close to wanted:', end=' ')
        print(four_score)
        print('to be kept:', end=' ')
        print(successful)
        print('total:', end=' ')
        print(successful + unsuccessful + four_score)
    except:
        print("error calculating score")

def combine_db():
    try:
        query = "select * from device_attributes_filtered;"
        cursor.execute(query)
        record = cursor.fetchall()
        for row in record:
            sqlStr = "insert ignore into device_attributes_combined(`Ref_DOI_number`,`Ref_lead_author`,`Ref_publication_date`,`Ref_title`," \
                             "`Ref_html_link`,`Cell_architecture`,`Cell_flexible`,`Substrate`,`Perovskite_composition`,`Perovskite_composition_short_form`," \
                             "`Perovskite_composition_a_ions`,`Perovskite_composition_a_ions_coefficients`,`Perovskite_composition_b_ions`," \
                             "`Perovskite_composition_b_ions_coefficients`,`Perovskite_composition_c_ions`,`Perovskite_composition_c_ions_coefficients`" \
                             ",`ETL`,`Top_contact`,`Top_contact_thickness`,`Top_contact_deposition`,`HTL`,`HTL_deposition`,`HTL_spin_coating_parameters`," \
                             "`HTL_annealing_parameters`,`ETL_deposition`,`ETL_spin_coating_parameters`,`ETL_annealing_parameters`,`Perovskite_deposition`,`Perovskite_spin_coating_parameters`,`Perovskite_annealing_parameters`)" \
                             "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" \
                             % (row['Ref_DOI_number'], row['Ref_lead_author'], row['Ref_publication_date'], row['Ref_title'],
                                row['Ref_html_link'], row['Cell_architecture'], row['Cell_flexible'], row['Substrate'],
                                row['Perovskite_composition'], row['Perovskite_composition_short_form'], row['Perovskite_composition_a_ions'],
                                row['Perovskite_composition_a_ions_coefficients'], row['Perovskite_composition_b_ions'],
                                row['Perovskite_composition_b_ions_coefficients'], row['Perovskite_composition_c_ions'], row['Perovskite_composition_c_ions_coefficients'],
                                row['ETL'], row['Top_contact'], row['Top_contact_thickness'], row['Top_contact_deposition'],
                                row['HTL'], row['HTL_deposition'], row['HTL_spin_coating_parameters'], row['HTL_annealing_parameters'],
                                row['ETL_deposition'], row['ETL_spin_coating_parameters'], row['ETL_annealing_parameters'], row['Perovskite_deposition'],
                                row['Perovskite_spin_coating_parameters'], row['Perovskite_annealing_parameters'])
            res = cursor.execute(sqlStr)
            conn.commit()
    except:
        print("error combining db")

if __name__ == '__main__':
    HTLs = ['spiro-ometad', 'spiro-meotad', 'pedot:pss', 'PTAA', 'NiO-c', 'P3HT', 'NiO-np', 'CuSCN', 'MoO3', 'NiO',
            'NiOx', 'polytpd', 'poly-tpd', 'nimglio', 'limgnio', 'NiO-mp', 'CuPc', 'p3ct-na', 'TaTm', 'PFN', 'CuI',
            'TAPC', 'MoOx', '2PACz', 'VOx', 'SWCNTs', 'PEDOT', 'P3CT-N', 'Cu2O', 'f6-tcnnq', 'rGO',
            'PTPD', 'al2o3-mp', 'MoS2', 'P3CT', 'al2o3-c', 'nimglio-c', 'PTB7', 'NPB', 'PCDTBT', 'P3CT-K',
            'PDBD-T', 'WO3', 'TPTPA', 'PDCBT', 'cupc(tbu)4', 'CuOx', 'CuO', 'CuS', 'TPD',
            '2tpa-2-dp', 'al2o3-mp', 'ttf1', 'pst1', 'ptpd2', 'ktm3', 'ptb7-th', 'fa-meoph', 'dmfa-fa', 'b[bmpdp]2', 'tt80', 'tips-pentacene', 'spiro-cpdt', 'jk-216d', 'hpdi', 'subpc', 'ha1', 'scpdt-bit', 'rgo', 'edot-ometpa',
            'th-pdi', 'triazine-flu', 'cualo2', 'azomethine', 'sym-htpch', 'rubrene', 'x60', 'p-or', 'polytpd', 'swcnts', 'ni-acetate', 'cui-np', 'mp-sfx-3pa', 'tpe-4dpa', 'bt41', 'q197', 'di-tpa', 'spiro-s', 'peh-3', 's101',
            'cu2basns4', 'ddof', 'hb-cz', 'a101', 'jy5', 'dly-1', 'pcbm-60', 'meo-datpa', 'nimglio', 'cupc', 'cuscn-3d', 'moo3', 'in2o3', 'cf-btz-thr', 'pah 1', 'v2o5', 'v2ox', 'pcpdtbt', 'sfd-spiro', 'moox', 'ptz-tpa', 'tdt-ometad',
            'btf1', '(octpho)8cupc1', 'acr-tpa', 'kr321', 'hl-1', 'cups-tips', 'sgt-405', 'cgs', 'pdme2pc', 'trux-e-t', 'cucro2', 'sitp-ometpa', 'ttpa-bdt', 'pqt-12', 'p3ct', 'tpd-4metpa', 'dpa-ant-dpa', 'x61', 'm104',
            'm107', 'vo', 'm:oo', 'pma', 'mc-43', 'asy-pbtbdt', 'edot-mph', 'sfx-tpam', 'x1', 'jw6', 'tq2', 'cdth 1', 'poly-tbd', 'h16', 'pbt', 'htm2', 'nipcs4', 'licoo2', 'sgo', 'tpa-qa-tpa', 'yn3', 'spiro-tbubed',
            'idtc6-tpa', 'cu3sbs4-np', 'v866', 'm-mtdata', 'v950', 'nipc', 'py-c', 'tae1', 'v1036', 'dfh', 'zn-chl', 'btf2', 'cu12sb4s13', 'cl1-2', 'pdo1', 'ph-tpa-2a', 'yt3', 'yk1', 'c201', 'tatm', 'bedn',
            'p3ct-n', 'btt-3', 'pt-dc', 'coth-ttpa', 'nico2o4', 'dtpc8-thdtpa', 'tpa-bp-oxd', 'z7', 't5h-omedpa']
    HTLs_mult = ['graphene oxide', 'spiro p-xylene', 'florinated polymer', 'tetra-substituted azulene',
                'cu phtalocyanine']
    ETLs = ['TiO2-c', 'TiO2-mp', 'PCBM', 'PCBM-60', 'PC60BM', 'PC61BM', 'C60', 'SnO2-c', 'SnO2-np', 'ZnO-c', 'ZnO-np', 'ZrO2-mp',
            'Bphen', 'al2o3-mp', 'TiO2-nw', 'TiO2-np', 'PEI', 'bis-C60', 'PCBM-70', 'ZnO-nw', 'C60-SAM',
            'zr(acac)4', 'AZO-np', 'TiO2', 'Nb2O5', 'CdS', 'SnO2', 'ZnO', 'PFN', 'SnO2-mp', 'PCBA', 'TiO2-nt',
            'Al2O3-c', 'AZO', 'ICBA', 'CPTA', 'ZnO-mp', 'MgO', 'C70', 'sno2-qds', 'TIPD',
            'tio2-nanofibers', 'SiO2-mp', 'F8TBT', 'carbon-qds', 'SrTiO3', 'Au-np', 'N2200',
            'AZO-c', 'Cs2CO3', 'In2O3-c', 'SnO2-nw', 'TiS2', 'ITIC', 'graphene-qds', 'NiO-np', 'carbon-mp', 'Ag-np',
            'Phlm', 'NiO-c', 'PDINO', 'PN4N', 'BACl', 'SiO2-np', 'tio2-nanosphere', 'TmPyPB', 'In2O3', 'SiO2-IO',
            'In2S3', 'ZTO', 'AAO', 'NDP-V', 'MgO-c', 'cdse-qds', 'IPH', 'Fe2O3', 'CeOx-np', 'phen-nadpo',
            'C60-N', 'PFN-Br', 'Nb2O5-c', 'PhIm', 'PTEG-1', 'itcptc-th', 'PCBSD', 'Alq3', 'Al2O3', 'itcptc-se',
            'ZnMgO', 'SWCNTs',
            'zn2sno4', 'pctdi', 'GaN', 'edta', 'cdse-qds', 'fpi-peie', 'zr(acac)4',
            'n-pdi', 'zn2sno4-c', 'ceox', 'pndi-2t', 'fe2o3', 'cds-np', 'in2o3', 'tdtp', 'h-pdi', 'a-dmec70', 'ndi-pm', 'nio-c', 'b2f', 'c60-sam', 'mc-43', 'pbzrtio3', 'tpe-pdi4', 'nbox', 'idtcn', 'cpta-e', 'tpe-dpp4', 'znso4-c', 'pfpdi', 'adahcl', 'srgeo3']
    ETLs_mult = ['rhodamine 101', 'rodhamine 101', '1-ethyl-3-methylimidazolium iodide', 'sinapoyl malate',
                 'trimethylamine oxide', 'graphene oxide', 's-acetylthiocholine chlorde',
                 'sno2 nanoparticle', '1‐benzyl‐3‐methylimidazolium chloride', 'black p-qds', 'caproic acid']
    html_files = get_htmls()
    data_insert_ref(html_files)
    txt_files = get_txts()
    data_insert_substrate(txt_files)
    data_insert_HTL(txt_files, HTLs, HTLs_mult)
    data_insert_ETL(txt_files, ETLs, ETLs_mult)
    data_insert_cell_architecture(txt_files)
    data_insert_perovskite_composition(txt_files)
    data_insert_deposition_method(txt_files)
    calculate_record_score()
    combine_db()