import re
import pandas as pd

def HTL_list():
    df = pd.read_csv("Perovskite_database_content_all_data.csv", usecols=["HTL_stack_sequence"])
    HTL = df["HTL_stack_sequence"]
    HTL_count = {}
    HTL_count_mult = {}
    for h in HTL:
        hl = re.split('\\||;', h)
        for item in hl:
            item = item.rstrip().lstrip()
            if len(item) > 6:
                item = item.lower()
            if item != 'none' and item != 'HTM' and len(item) > 2:
                if ' ' not in item:
                    if item in HTL_count:
                        HTL_count[item] += 1
                    else:
                        HTL_count[item] = 1
                else:
                    if item in HTL_count_mult:
                        HTL_count_mult[item] += 1
                    else:
                        HTL_count_mult[item] = 1
    HTL_list = ['spiro-ometad'] + sorted(HTL_count, key=HTL_count.get, reverse=True)
    HTL_list_mult = sorted(HTL_count_mult, key=HTL_count_mult.get, reverse=True)
    HTL_list.remove('PbI2')
    return HTL_list

def HTL_mining(para, HTL_list, HTL_list_mult):
    # HTL_details is a list containing all the HTLs that are in the paragraph
    HTL_details = []
    for x in range(len(para.sentences)):
        words = re.split('/| ', para.sentences[x].text)
        for index in range(len(words)-1):
            word = words[index].replace(',', '').replace('(', '').replace(')', '')
            mult = str(words[index] + ' ' + words[index+1]).lower().replace(',', '').replace('(', '').replace(')', '')
            if mult in HTL_list_mult:
                HTL_details.append(mult)
            if len(word) > 6:
                word = word.lower()
            if word in HTL_list:
                HTL_details.append(word)
    return HTL_details

def ETL_list():
    df = pd.read_csv("Perovskite_database_content_all_data.csv", usecols=["ETL_stack_sequence"])
    ETL = df["ETL_stack_sequence"]
    ETL_count = {}
    ETL_count_mult = {}
    for e in ETL:
        el = re.split('\\||;', e)
        for item in el:
            item = item.rstrip().lstrip()
            if len(item) > 7:
                item = item.lower()
            if item != 'none' and item != 'ETM' and len(item) > 2:
                if ' ' not in item:
                    if item in ETL_count:
                        ETL_count[item] += 1
                    else:
                        ETL_count[item] = 1
                else:
                    if item in ETL_count_mult:
                        ETL_count_mult[item] += 1
                    else:
                        ETL_count_mult[item] = 1
    ETL_list = sorted(ETL_count, key=ETL_count.get, reverse=True)
    ETL_list_mult = sorted(ETL_count_mult, key=ETL_count_mult.get, reverse=True)
    return ETL_list

def ETL_mining(para, ETL_list, ETL_list_mult):
    ETL_details = []
    for x in range(len(para.sentences)):
        words = re.split('/| ', para.sentences[x].text)
        for index in range(len(words)-1):
            word = words[index].replace(',', '').replace('(', '').replace(')', '')
            mult = str(words[index] + ' ' + words[index+1]).lower().replace(',', '').replace('(', '').replace(')', '')
            if mult in ETL_list_mult:
                ETL_details.append(mult)
            if len(word) > 6:
                word = word.lower()
            if word in ETL_list:
                ETL_details.append(word)
    return ETL_details

def cell_stack_mining(para):
    cell_stack = ''
    for x in range(len(para.sentences)):
        for y in range(len(para.sentences[x].tokens)):
            if para.sentences[x].tokens[y].text == '/':
                chems = []
                for chemical in para.sentences[x].cems:
                    chems.append(chemical.text)
                try:
                    count_slash = 1
                    count_cems = 0
                    last_slash_index = 0
                    for z in range(1, 15):
                        if para.sentences[x].tokens[y + z].text == '/':
                            count_slash += 1
                        elif para.sentences[x].tokens[y + z].text in chems:
                            count_cems += 1
                    if count_slash > 3 and count_cems > 1:
                        last_token = len(para.sentences[x].tokens) - y
                        for z in range(1, min(50, last_token)):
                            if para.sentences[x].tokens[y + z].text == '/':
                                last_slash_index = z
                        for ind in range(0, last_slash_index + 3):
                            if para.sentences[x].pos_tagged_tokens[y + ind - 1][1] == 'IN' \
                                    or para.sentences[x].pos_tagged_tokens[y + ind - 1][1] == 'WRB' \
                                    or para.sentences[x].pos_tagged_tokens[y + ind - 1][1] == 'VBZ' \
                                    or para.sentences[x].pos_tagged_tokens[y + ind - 1][0] == 'and':
                                return ''
                            if ind == 0 and para.sentences[x].tokens[y + ind - 1].text == ')':
                                ind2 = 1
                                open_bracket = 0
                                while True:
                                    if para.sentences[x].tokens[y + ind - ind2 - 1].text == '(':
                                        open_bracket = 1
                                    if para.sentences[x].tokens[y + ind - ind2 - 1].text in chems:
                                        break
                                    ind2 += 1
                                while ind2 >= 1:
                                    cell_stack += para.sentences[x].tokens[y + ind - ind2 - 1].text
                                    cell_stack += ' '
                                    ind2 -= 1
                                if open_bracket == 1:
                                    cell_stack += para.sentences[x].tokens[y + ind - 1].text
                                    cell_stack += ' '
                            else:
                                cell_stack += para.sentences[x].tokens[y + ind - 1].text
                                cell_stack += ' '
                        if para.sentences[x].tokens[y + last_slash_index + 3].text in chems:
                            cell_stack += para.sentences[x].tokens[y + last_slash_index + 3].text
                        break
                except:
                    break
    return cell_stack.rstrip()

def substrate_mining(para):
    all_substrates = []
    flexible = 0
    for x in range(len(para.sentences)):
        for y in range(len(para.sentences[x].tokens)):
            if para.sentences[x].tokens[y].text.upper() == 'FTO' or para.sentences[x].tokens[y].text.upper() == 'ITO':
                all_substrates.append(para.sentences[x].tokens[y].text.upper())
            elif para.sentences[x].tokens[y].text.upper() == 'PET' or para.sentences[x].tokens[y].text.upper() == 'PEN':
                all_substrates.append(para.sentences[x].tokens[y].text.upper())
                flexible = 1
    return all_substrates, flexible

def perovskite_composition_mining(para):
    perovskite_composition = ''
    for x in range(len(para.sentences)):
        for y in range(len(para.sentences[x].tokens)):
            ion_presence = [0, 0, 0, 0]    # presence of A, B, X, and absence of irregularities such as Br3-xIx
            for a_i in ['Cs', 'FA', 'MA', 'CH3NH3', 'H3CNH3', 'CH(NH2)2', 'HC(NH2)2', 'GU', 'BA', 'PEA']:
                if a_i in para.sentences[x].tokens[y].text:
                    ion_presence[0] = 1
            for b_i in ['Pb', 'Sn', 'Bi', 'Ag', 'Na', 'Ge']:
                if b_i in para.sentences[x].tokens[y].text:
                    ion_presence[1] = 1
            for c_i in ['Br', 'Cl', 'I', 'SCN']:
                if c_i in para.sentences[x].tokens[y].text:
                    ion_presence[2] = 1
            if 'x' not in para.sentences[x].tokens[y].text and 'X' not in para.sentences[x].tokens[y].text and 'y' not in para.sentences[x].tokens[y].text:
                ion_presence[3] = 1
            if ion_presence == [1, 1, 1, 1] and '{' not in para.sentences[x].tokens[y].text\
                    and not (')' in para.sentences[x].tokens[y].text and '(' not in para.sentences[x].tokens[y].text):
                perovskite_composition = (para.sentences[x].tokens[y].text).replace('CH(NH2)2', 'FA').replace('HC(NH2)2', 'FA').replace('CH3NH3', 'MA').replace('H3CNH3', 'MA')
                return perovskite_composition
    return perovskite_composition

def perovskite_ratio(perovskite_composition):
    perovskite_composition = perovskite_composition.replace("[", "(").replace("]", ")").replace("+", "").replace("-", "")
    ABX_total_value = [0, 0, 0]     # should be [1, 1, 3] or [2, 2, 6]
    ABX = [[], [], []]
    ABX_ratio = [[], [], []]
    short_form = ''
    long_form_modified = ''
    val = 1
    current_string = ''
    multiply = 1.0
    while val <= len(perovskite_composition):
        if perovskite_composition[len(perovskite_composition)-val] == ')':
            try:
                multiply = float(current_string)
            except:
                return [[], [], []], [[], [], []], '', ''
            current_string = ''
        elif perovskite_composition[len(perovskite_composition)-val] == '(':
            multiply = 1.0
        else:
            current_string = perovskite_composition[len(perovskite_composition) - val] + current_string
        try:
            for c_i in ['Br', 'Cl', 'I', 'SCN']:
                if current_string.startswith(c_i):
                    ABX[2].append(c_i)
                    short_form = c_i + short_form
                    if current_string.removeprefix(c_i) == '':
                        ABX_ratio[2].append(multiply)
                        ABX_total_value[2] += multiply
                        long_form_modified = c_i + str(multiply) + long_form_modified
                    else:
                        ABX_ratio[2].append(round(float(current_string.removeprefix(c_i))*multiply, 2))
                        ABX_total_value[2] += round(float(current_string.removeprefix(c_i))*multiply, 2)
                        long_form_modified = c_i + str(round(float(current_string.removeprefix(c_i))*multiply, 2)) + long_form_modified
                    current_string = ''
            for b_i in ['Pb', 'Sn', 'Bi', 'Ag', 'Na', 'Ge']:
                if current_string.startswith(b_i):
                    ABX[1].append(b_i)
                    short_form = b_i + short_form
                    if current_string.removeprefix(b_i) == '':
                        ABX_ratio[1].append(multiply)
                        ABX_total_value[1] += multiply
                        long_form_modified = b_i + str(multiply) + long_form_modified
                    else:
                        ABX_ratio[1].append(round(float(current_string.removeprefix(b_i))*multiply, 2))
                        ABX_total_value[1] += round(float(current_string.removeprefix(b_i))*multiply, 2)
                        long_form_modified = b_i + str(round(float(current_string.removeprefix(b_i))*multiply, 2)) + long_form_modified
                    current_string = ''
            for a_i in ['Cs', 'FA', 'MA', 'GU', 'BA', 'PEA']:
                if current_string.startswith(a_i):
                    ABX[0].append(a_i)
                    short_form = a_i + short_form
                    if current_string.removeprefix(a_i) == '':
                        ABX_ratio[0].append((multiply))
                        ABX_total_value[0] += multiply
                        long_form_modified = a_i + str(multiply) + long_form_modified
                    else:
                        ABX_ratio[0].append((round(float(current_string.removeprefix(a_i))*multiply, 2)))
                        ABX_total_value[0] += round(float(current_string.removeprefix(a_i))*multiply, 2)
                        long_form_modified = a_i + str(round(float(current_string.removeprefix(a_i))*multiply, 2)) + long_form_modified
                    current_string = ''
        except:
            return [[], [], []], [[], [], []], '', ''
        val += 1
    return ABX, ABX_ratio, short_form, long_form_modified

def top_contact_mining(sen):
    top_contact_identified = ''
    thickness = ''
    top_contact_list = ['Au', 'gold', 'Ag', 'silver', 'Cu', 'copper', 'carbon', 'graphite', 'Al', 'aluminum', 'aluminium']
    words = re.split('/| |-', sen)
    for index in range(len(words)-1):
        word = words[index].replace(',', '').replace('(', '').replace(')', '')
        if len(word) > 3:
            word = word.lower()
        if word in top_contact_list:
            top_contact_identified = word
            if 'nm ' in sen or 'nm)' in sen or 'nm-' in sen or '-nm' in sen:
                predicted_thickness = (sen.split("nm")[-2].rstrip().replace('-', '').replace('(', '')).split()[-1]
                try:
                    if int(predicted_thickness) < 10:
                        print('wrong thickness:' + str(int(predicted_thickness)) + " nm")
                        print(sen)
                    else:
                        thickness = str(int(predicted_thickness)) + " nm"
                except:
                    pass
    return top_contact_identified, thickness

def cell_architecture_mining(para, materials):
    cell_architecture = 0   # 1 if nip, 2 if pin
    if materials['HTL'] != '':
        if 'spiro' in materials['HTL'].lower():
            cell_architecture = 1
        elif 'nio' in materials['HTL'].lower() or 'pedot' in materials['HTL'].lower():
            cell_architecture = 2
    index_PVK = -1
    index_HTL = -1
    if cell_architecture == 0:
        for x in range(len(para.sentences)):
            tx = para.sentences[x].text
            HTL_list = [materials['HTL'], ' HTM ', ' HTL ', 'hole transport', 'hole-transport', 'hole conductor',
                        'hole extraction', 'hole selective', 'hole-selective']
            if 'deposit' in tx.lower() or 'spin' in tx.lower():
                for item in HTL_list:
                    if item in tx:
                        index_HTL = x
                if 'perovskite' in tx:
                    index_PVK = x
        if index_HTL != -1 and index_PVK != -1:
            if index_HTL > index_PVK:
                cell_architecture = 1
            elif index_HTL < index_PVK:
                cell_architecture = 2
    return cell_architecture

def deposition_method_mining(para, materials):
    deposition_method = {'top contact': '', 'HTL': '', 'perovskite': '', 'ETL': ''}
    method_material_list = {'HTL': ['HTM', 'HTL', 'hole transport', 'hole-transport'],
                            'perovskite': ['perovskite', 'PbI2', 'FA', 'MA', 'CH3NH3', 'H3CNH3', 'CH(NH2)2',
                                           'HC(NH2)2'],
                            'ETL': ['ETM', 'ETL', 'electron transport', 'electron-transport']}
    if materials['HTL'] != '':
        method_material_list['HTL'] = [materials['HTL'], ' HTM ', ' HTL ', 'hole transport',
                                       'hole-transport', 'hole conductor', 'hole extraction',
                                       'hole selective', 'hole-selective']
        if 'pedot' in materials['HTL'].lower():
            method_material_list['HTL'].append('pedot')
    if materials['ETL'] != '':
        method_material_list['ETL'] = [materials['ETL'], 'ETM', 'ETL', 'electron transport',
                                       'electron-transport', 'electron conductor',
                                       'electron selective', 'electron-selective']
    top_contact = ''
    top_contact_original = ''
    top_contact_thickness = ''
    HTL_spin_coat_parameters = []
    HTL_anneal_parameters = []
    ETL_spin_coat_parameters = []
    ETL_anneal_parameters = []
    perovskite_spin_coat_parameters = []
    perovskite_anneal_parameters = []
    for key in deposition_method:
        for x in range(len(para.sentences)):
            tx = para.sentences[x].text
            if key == 'top contact':
                if 'evaporat' in tx.lower() or 'thermal' in tx.lower() or 'mask' in tx.lower() or 'vacuum chamber' in tx.lower() \
                        or ('Å' in tx and ('s-1' in tx or '/s' in tx)) or 'electrode' in tx \
                        or 'sputter' in tx.lower() or (('carbon' in tx.lower() or 'graphite' in tx.lower())
                                                       and (
                                                               'laminat' in tx.lower() or 'screen' in tx.lower() or 'pulsed laser' in tx.lower()
                                                               or 'PLD' in tx.lower() or 'doctor' in tx.lower() or 'spray' in tx.lower())):
                    deposition_material, thickness = top_contact_mining(tx)
                    top_contact_original = deposition_material
                    if deposition_material != '':
                        if top_contact_thickness == '' and thickness != '':
                            top_contact_thickness = thickness
                        if deposition_material == 'gold' or deposition_material == 'Au':
                            top_contact = 'Au'
                            if top_contact_thickness == '':
                                top_contact_thickness = '60-100 nm'
                        elif deposition_material == 'silver' or deposition_material == 'Ag':
                            top_contact = 'Ag'
                            if top_contact_thickness == '':
                                top_contact_thickness = '80-120 nm'
                        elif deposition_material == 'copper':
                            top_contact = 'Cu'
                        elif deposition_material == 'aluminum' or deposition_material == 'aluminium':
                            top_contact = 'Al'
                        else:
                            top_contact = deposition_material
                        top_contact_list = ['Au', 'Ag', 'Cu', 'Al']
                        if 'sputter' in tx.lower() and 'evaporat' not in tx.lower():
                            deposition_method[key] = 'Sputtering'
                        elif top_contact in top_contact_list or 'evaporat' in tx or 'thermal' in tx or \
                                'mask' in tx or ('Å' in tx and ('s-1' in tx or '/s' in tx)):
                            deposition_method[key] = 'Evaporation'
                        else:
                            other_keyword = ['laminat', 'screen print', 'screen-print', 'pulsed laser', 'PLD',
                                             'doctor blad', 'doctor-blad', 'spray-coat', 'spray coat',
                                             'blade-coat', 'blade coat', 'blading', 'bladed']
                            other_method = ['Lamination', 'Screen printing', 'Screen printing',
                                            'Pulsed laser deposition', 'Pulsed laser deposition',
                                            'Doctor blading', 'Doctor blading', 'Spray-coating', 'Spray-coating',
                                            'Doctor blading', 'Doctor blading', 'Doctor blading', 'Doctor blading']
                            method_count = 0
                            for indx in range(len(other_method)):
                                if other_keyword[indx] in tx.lower():
                                    if deposition_method[key] == '' or deposition_method[key] == other_method[indx]:
                                        deposition_method[key] = other_method[indx]
                                    else:
                                        method_count += 1
                            if method_count >= 1:
                                deposition_method[key] = ''
                else:
                    top_contact_pred = ['/Au', '/gold', '/Ag', '/silver', '/Cu', '/copper', '/Cr', '/Al', '/aluminum',
                                        '/aluminium']
                    for word in tx.split():
                        for ending in top_contact_pred:
                            if word.endswith(ending) and top_contact != '':
                                top_contact = ending[1:]
                                deposition_material, thickness = top_contact_mining(tx)
                                top_contact_original = top_contact
                                if top_contact_thickness == '' and thickness != '':
                                    top_contact_thickness = thickness
                                if top_contact == 'gold' or top_contact == 'Au':
                                    top_contact = 'Au'
                                    if top_contact_thickness == '':
                                        top_contact_thickness = '80-100 nm'
                                elif top_contact == 'silver' or top_contact == 'Ag':
                                    top_contact = 'Ag'
                                    if top_contact_thickness == '':
                                        top_contact_thickness = '100-120 nm'
                                elif top_contact == 'copper':
                                    top_contact = 'Cu'
                                elif top_contact == 'aluminum' or top_contact == 'aluminium':
                                    top_contact = 'Al'
                                deposition_method[key] = 'Evaporation'
                                break
            if key == 'HTL' and deposition_method[key] == '':
                if 'spin-coat' in tx.lower() or 'spin coat' in tx.lower() or 'spincoat' in tx.lower() or \
                        'spin-cast' in tx.lower() or 'spun' in tx.lower() or \
                        (('rpm' in tx or 'r.p.m' in tx) and 's' in tx):
                    index_material = -1
                    for item in method_material_list[key]:
                        if len(item) > 3:
                            if tx.lower().find(item.lower()) != -1:
                                index_material = tx.lower().find(item.lower())
                                break
                        elif len(item) <= 3:
                            if tx.find(item) != -1:
                                index_material = tx.find(item)
                                break
                    if index_material == -1:
                        if tx.lower().find('solution') != -1 and x > 0:
                            previous_sen = para.sentences[x - 1].text
                            for item in method_material_list[key]:
                                if len(item) > 3:
                                    if previous_sen.lower().find(item.lower()) != -1:
                                        index_material = tx.lower().find('solution')
                                        break
                                elif len(item) <= 3:
                                    if previous_sen.find(item) != -1:
                                        index_material = tx.lower().find('solution')
                                        break
                    if index_material != -1:
                        index_on = -1
                        if tx.find(' on ') != -1:
                            index_on = tx.lower().find(' on ')
                        elif tx.find(' onto ') != -1:
                            index_on = tx.lower().find(' onto ')
                        if index_material < index_on or index_on == -1:
                            deposition_method[key] = 'Spin-coating'
                            spin_coat_parameter = spin_coat_mining(para.sentences[x], method_material_list[key])
                            anneal_parameter = anneal_mining(para.sentences[x])
                            if x < len(para.sentences) - 1 and anneal_parameter == []:
                                if 'anneal' in para.sentences[x + 1].text or 'hotplate' in para.sentences[x + 1].text:
                                    anneal_parameter = anneal_mining(para.sentences[x + 1])
                            if spin_coat_parameter != []:
                                if spin_coat_parameter[0] != [] and spin_coat_parameter[1] != []:
                                    HTL_spin_coat_parameters = [spin_coat_parameter[0], spin_coat_parameter[1]]
                            if anneal_parameter != []:
                                if anneal_parameter[0] != [] and anneal_parameter[1] != []:
                                    HTL_anneal_parameters = anneal_parameter
                else:
                    keyword = ['doctor blad', 'doctor-blad', 'bladed', 'blade-coat', 'blading', 'blade coat',
                               'inkjet', 'ink-jet', 'slot-die', 'slot die', ' ald ', 'atomic layer deposit',
                               ' cbd ', 'chemical bath deposit', 'dip-coat', 'dip coat', 'drop cast',
                               'electrodeposit', 'evaporat', 'spray pyrolys', 'sputter']
                    method = ['Doctor blading', 'Doctor blading', 'Doctor blading', 'Doctor blading', 'Doctor blading',
                              'Doctor blading',
                              'Inkjet printing', 'Inkjet printing', 'Slot-die coating', 'Slot-die coating', 'ALD',
                              'ALD',
                              'CBD', 'CBD', 'Dip-coating', 'Dip-coating', 'Drop casting',
                              'Electrodeposition', 'Evaporation', 'Spray pyrolysis', 'Sputtering']
                    for indx in range(len(method)):
                        if keyword[indx] in tx.lower():
                            if deposition_method[key] == '' or deposition_method[key] == method[indx]:
                                index_material = -1
                                index_transport_layer = -1
                                for item in method_material_list[key]:
                                    if len(item) > 3:
                                        if tx.lower().find(item.lower()) != -1:
                                            index_material = tx.lower().find(item.lower())
                                            break
                                    elif len(item) <= 3:
                                        if tx.find(item) != -1:
                                            index_material = tx.find(item)
                                            break
                                if index_material == -1:
                                    sol = ['solution', 'mixture']
                                    for so in sol:
                                        if tx.lower().find(so) != -1 and x > 0:
                                            previous_sen = para.sentences[x - 1].text
                                            for item in method_material_list[key]:
                                                if len(item) > 3:
                                                    if previous_sen.lower().find(item.lower()) != -1:
                                                        index_material = tx.lower().find(so)
                                                        break
                                                elif len(item) <= 3:
                                                    if previous_sen.find(item) != -1:
                                                        index_material = tx.lower().find(so)
                                                        break
                                for item in method_material_list['perovskite']:
                                    if tx.lower().find(item.lower()) != -1:
                                        index_transport_layer = tx.lower().find(item.lower())
                                        break
                                for item in ['electrode', top_contact_original, 'ITO']:
                                    if (len(item) > 3 and tx.lower().find(item.lower()) != -1) \
                                            or (len(item) <= 3 and tx.find(item) != -1):
                                        index_material = -1
                                        break
                                if index_material != -1:
                                    index_on = -1
                                    index_comma = -1
                                    if tx.find('On ') != -1:
                                        index_on = tx.find('On ')
                                    if tx.find('After ') != -1:
                                        index_on = tx.find('After ')
                                    elif tx.find(' on ') != -1:
                                        index_on = tx.lower().find(' on ')
                                    elif tx.find(' onto ') != -1:
                                        index_on = tx.lower().find(' onto ')
                                    if tx.find(', ') != -1:
                                        index_comma = tx.lower().find(', ')
                                    if index_transport_layer == -1 \
                                            or (
                                            index_on < index_transport_layer and index_transport_layer < index_comma and index_comma < index_material) \
                                            or (index_material < index_on and index_on < index_transport_layer):
                                        deposition_method[key] = method[indx]
                                        break
            if key == 'ETL' and deposition_method[key] == '':
                if 'spin-coat' in tx.lower() or 'spin coat' in tx.lower() or 'spincoat' in tx.lower() or \
                        'spin-cast' in tx.lower() or 'spun' in tx.lower() or \
                        (('rpm' in tx or 'r.p.m' in tx) and 's' in tx):
                    index_material = -1
                    for item in method_material_list[key]:
                        if len(item) > 3:
                            if tx.lower().find(item.lower()) != -1:
                                index_material = tx.lower().find(item.lower())
                                break
                        elif len(item) <= 3:
                            if tx.find(item) != -1:
                                index_material = tx.find(item)
                                break
                    if index_material == -1:
                        if tx.lower().find('solution') != -1 and x > 0:
                            previous_sen = para.sentences[x - 1].text
                            for item in method_material_list[key]:
                                if len(item) > 3:
                                    if previous_sen.lower().find(item.lower()) != -1:
                                        index_material = tx.lower().find('solution')
                                        break
                                elif len(item) <= 3:
                                    if previous_sen.find(item) != -1:
                                        index_material = tx.lower().find('solution')
                                        break
                    if index_material != -1:
                        index_on = -1
                        if tx.find(' on ') != -1:
                            index_on = tx.lower().find(' on ')
                        elif tx.find(' onto ') != -1:
                            index_on = tx.lower().find(' onto ')
                        if index_material < index_on or index_on == -1:
                            deposition_method[key] = 'Spin-coating'
                            spin_coat_parameter = spin_coat_mining(para.sentences[x], method_material_list[key])
                            anneal_parameter = anneal_mining(para.sentences[x])
                            if x < len(para.sentences) - 1 and anneal_parameter == []:
                                if 'anneal' in para.sentences[x + 1].text or 'hotplate' in para.sentences[x + 1].text:
                                    anneal_parameter = anneal_mining(para.sentences[x + 1])
                            if spin_coat_parameter != []:
                                if spin_coat_parameter[0] != [] and spin_coat_parameter[1] != []:
                                    ETL_spin_coat_parameters = [spin_coat_parameter[0], spin_coat_parameter[1]]
                            if anneal_parameter != []:
                                if anneal_parameter[0] != [] and anneal_parameter[1] != []:
                                    ETL_anneal_parameters = anneal_parameter
                else:
                    keyword = ['doctor blad', 'doctor-blad', 'bladed', 'blade-coat', 'blading', 'blade coat',
                               'inkjet', 'ink-jet', 'slot-die', 'slot die', ' ald ', 'atomic layer deposit',
                               ' cbd ', 'chemical bath deposit', 'dip-coat', 'dip coat', 'drop cast',
                               'electrodeposit', 'evaporat', 'spray pyrolys', 'sputter']
                    method = ['Doctor blading', 'Doctor blading', 'Doctor blading', 'Doctor blading', 'Doctor blading', 'Doctor blading',
                              'Inkjet printing', 'Inkjet printing', 'Slot-die coating', 'Slot-die coating', 'ALD',
                              'ALD', 'CBD', 'CBD', 'Dip-coating', 'Dip-coating', 'Drop casting',
                              'Electrodeposition', 'Evaporation', 'Spray pyrolysis', 'Sputtering']
                    for indx in range(len(method)):
                        if keyword[indx] in tx.lower():
                            if deposition_method[key] == '' or deposition_method[key] == method[indx]:
                                index_material = -1
                                index_transport_layer = -1
                                for item in method_material_list[key]:
                                    if len(item) > 3:
                                        if tx.lower().find(item.lower()) != -1:
                                            index_material = tx.lower().find(item.lower())
                                            break
                                    elif len(item) <= 3:
                                        if tx.find(item) != -1:
                                            index_material = tx.find(item)
                                            break
                                if index_material == -1:
                                    sol = ['solution', 'mixture']
                                    for so in sol:
                                        if tx.lower().find(so) != -1 and x > 0:
                                            previous_sen = para.sentences[x - 1].text
                                            for item in method_material_list[key]:
                                                if len(item) > 3:
                                                    if previous_sen.lower().find(item.lower()) != -1:
                                                        index_material = tx.lower().find(so)
                                                        break
                                                elif len(item) <= 3:
                                                    if previous_sen.find(item) != -1:
                                                        index_material = tx.lower().find(so)
                                                        break
                                for item in method_material_list['perovskite']:
                                    if tx.lower().find(item.lower()) != -1:
                                        index_transport_layer = tx.lower().find(item.lower())
                                        break
                                for item in ['electrode', top_contact_original,
                                             'ITO']:
                                    if (len(item) > 3 and tx.lower().find(item.lower()) != -1) \
                                            or (len(item) <= 3 and tx.find(item) != -1):
                                        index_material = -1
                                        break
                                if index_material != -1:
                                    index_on = -1
                                    index_comma = -1
                                    if tx.find('On ') != -1:
                                        index_on = tx.find('On ')
                                    if tx.find('After ') != -1:
                                        index_on = tx.find('After ')
                                    elif tx.find(' on ') != -1:
                                        index_on = tx.lower().find(' on ')
                                    elif tx.find(' onto ') != -1:
                                        index_on = tx.lower().find(' onto ')
                                    if tx.find(', ') != -1:
                                        index_comma = tx.lower().find(', ')
                                    if index_transport_layer == -1 \
                                            or (index_on < index_transport_layer and index_transport_layer < index_comma and index_comma < index_material) \
                                            or (index_material < index_on and index_on < index_transport_layer):
                                        deposition_method[key] = method[indx]
                                        break
            if key == 'perovskite' and deposition_method[key] == '':
                if 'spin-coat' in tx.lower() or 'spin coat' in tx.lower() or 'spincoat' in tx.lower() or \
                        'spin-cast' in tx.lower() or 'spun' in tx.lower() or \
                        (('rpm' in tx or 'r.p.m' in tx) and 's' in tx):
                    index_material = -1
                    index_transport_layer = -1
                    for item in method_material_list[key]:
                        if len(item) > 3:
                            if tx.lower().find(item.lower()) != -1:
                                index_material = tx.lower().find(item.lower())
                                break
                        elif len(item) <= 3:
                            if tx.find(item) != -1:
                                index_material = tx.find(item)
                                break
                    if index_material == -1:
                        sol = ['solution', 'precursor']
                        for so in sol:
                            if tx.lower().find(so) != -1 and x > 0:
                                previous_sen = para.sentences[x - 1].text
                                for item in method_material_list[key]:
                                    if len(item) > 3:
                                        if previous_sen.lower().find(item.lower()) != -1:
                                            index_material = tx.lower().find(so)
                                            break
                                    elif len(item) <= 3:
                                        if previous_sen.find(item) != -1:
                                            index_material = tx.lower().find(so)
                                            break
                    for item in method_material_list['HTL'] + method_material_list['ETL']:
                        if tx.lower().find(item.lower()) != -1:
                            index_transport_layer = tx.lower().find(item.lower())
                            break
                    if index_material != -1:
                        index_on = -1
                        index_comma = -1
                        if tx.find('On ') != -1:
                            index_on = tx.find('On ')
                        if tx.find('After ') != -1:
                            index_on = tx.find('After ')
                        elif tx.find(' on ') != -1:
                            index_on = tx.lower().find(' on ')
                        elif tx.find(' onto ') != -1:
                            index_on = tx.lower().find(' onto ')
                        if tx.find(', ') != -1:
                            index_comma = tx.lower().find(', ')
                        if index_transport_layer == -1 \
                                or (
                                index_on < index_transport_layer and index_transport_layer < index_comma and index_comma < index_material) \
                                or (index_material < index_on and index_on < index_transport_layer):
                            deposition_method[key] = 'Spin-coating'
                            spin_coat_parameter = spin_coat_mining(para.sentences[x], method_material_list[key])
                            anneal_parameter = anneal_mining(para.sentences[x])
                            if x < len(para.sentences) - 1 and anneal_parameter == []:
                                if 'anneal' in para.sentences[x + 1].text or 'hotplate' in para.sentences[
                                    x + 1].text or 'heat' in para.sentences[x + 1].text:
                                    anneal_parameter = anneal_mining(para.sentences[x + 1])
                            if spin_coat_parameter != []:
                                if spin_coat_parameter[0] != [] and spin_coat_parameter[1] != []:
                                    perovskite_spin_coat_parameters = [spin_coat_parameter[0], spin_coat_parameter[1]]
                            if anneal_parameter != []:
                                if anneal_parameter[0] != [] and anneal_parameter[1] != []:
                                    perovskite_anneal_parameters = anneal_parameter
                else:
                    keyword = ['doctor blad', 'doctor-blad', 'bladed', 'blade-coat', 'blading', 'blade coat',
                               'inkjet', 'ink-jet', 'slot-die', 'slot die', 'electrodeposit', 'electro deposit',
                               'electro-deposit']
                    method = ['Doctor blading', 'Doctor blading', 'Doctor blading', 'Doctor blading', 'Doctor blading',
                              'Doctor blading',
                              'Inkjet printing', 'Inkjet printing', 'Slot-die coating', 'Slot-die coating',
                              'Electrodeposition', 'Electrodeposition', 'Electrodeposition']
                    for indx in range(len(method)):
                        if keyword[indx] in tx.lower():
                            if deposition_method[key] == '' or deposition_method[key] == method[indx]:
                                index_material = -1
                                index_transport_layer = -1
                                for item in method_material_list[key]:
                                    if len(item) > 3:
                                        if tx.lower().find(item.lower()) != -1:
                                            index_material = tx.lower().find(item.lower())
                                            break
                                    elif len(item) <= 3:
                                        if tx.find(item) != -1:
                                            index_material = tx.find(item)
                                            break
                                if index_material == -1:
                                    if tx.lower().find('solution') != -1 and x > 0:
                                        previous_sen = para.sentences[x - 1].text
                                        for item in method_material_list[key]:
                                            if len(item) > 3:
                                                if previous_sen.lower().find(item.lower()) != -1:
                                                    index_material = tx.lower().find('solution')
                                                    break
                                            elif len(item) <= 3:
                                                if previous_sen.find(item) != -1:
                                                    index_material = tx.lower().find('solution')
                                                    break
                                for item in method_material_list['HTL'] + method_material_list['ETL'] + ['electrode',
                                                                                                         top_contact_original]:
                                    if len(item) > 3:
                                        if tx.lower().find(item.lower()) != -1:
                                            index_transport_layer = tx.lower().find(item.lower())
                                            break
                                    elif len(item) <= 3:
                                        if tx.find(item) != -1:
                                            index_transport_layer = tx.find(item)
                                            break
                                if index_material != -1:
                                    index_on = -1
                                    index_comma = -1
                                    if tx.find('On ') != -1:
                                        index_on = tx.find('On ')
                                    if tx.find('After ') != -1:
                                        index_on = tx.find('After ')
                                    elif tx.find(' on ') != -1:
                                        index_on = tx.lower().find(' on ')
                                    elif tx.find(' onto ') != -1:
                                        index_on = tx.lower().find(' onto ')
                                    if tx.find(', ') != -1:
                                        index_comma = tx.lower().find(', ')
                                    if index_transport_layer == -1 \
                                            or (
                                            index_on < index_transport_layer and index_transport_layer < index_comma and index_comma < index_material) \
                                            or (index_material < index_on and index_on < index_transport_layer):
                                        deposition_method[key] = method[indx]
                                        break
    return top_contact, top_contact_thickness, deposition_method, HTL_spin_coat_parameters, HTL_anneal_parameters, \
           perovskite_spin_coat_parameters, perovskite_anneal_parameters, ETL_spin_coat_parameters, ETL_anneal_parameters

def spin_coat_mining(sen, material_list): # todo revolutions per minute
    final_spin_coat = []
    spin_coat = [[], [], [], []]    # speed, duration, material, material it is deposited onto
    if ('spin-coat' in sen.text or 'spin coat' in sen.text or 'spincoat' in sen.text
        or (('rpm' in sen.text or 'r.p.m' in sen.text) and 's' in sen.text)) and 'evaporat' not in sen.text and 'soak' not in sen.text:
        # todo deal with 3000rpm. TRY f.py
        tok = sen.tokens
        spin_mark = []
        multiple = 0
        on_mark = [0, 0]      # begin, end
        for word_mark in range(len(tok)):
            spin_coating_unit = ['s', 'min', 'h', 'seconds', 'minutes']
            if 'on' == tok[word_mark].text or 'onto' == tok[word_mark].text:
                on_mark[0] = word_mark
            elif 'film' == tok[word_mark].text or 'substrate' == tok[word_mark].text:
                if on_mark[0] != 0 and word_mark > on_mark[0]:
                    on_mark[1] = word_mark
            if 'rpm' == tok[word_mark].text or 'r.p.m.' == tok[word_mark].text or 'r.p.m' == tok[word_mark].text:
                mult_rpm = []
                try:
                    dig = int(tok[word_mark - 1].text.replace(',', ''))
                    mult_rpm.append(dig)
                    spin_mark.append(word_mark)
                    n = 2
                    while True:
                        if tok[word_mark - n].text != 'and' and tok[word_mark - n].text != ',':
                            break
                        try:
                            dig = int(tok[word_mark - n - 1].text.replace(',', ''))
                            mult_rpm.append(dig)
                            multiple = 1
                        except:
                            pass
                        n += 2
                except:
                    pass
                for ids in range(len(mult_rpm)):
                    spin_coat[0].append(mult_rpm[len(mult_rpm)-1-ids])
            elif 'rpm' in tok[word_mark].text or 'r.p.m.' in tok[word_mark].text or 'r.p.m' in tok[word_mark].text:
                split_t = 'rpm' # todo for duration, confirm that it is only an integer with that 's', etc..
                if 'r.p.m' in tok[word_mark].text:
                    split_t = 'r.p.m'
                mult_rpm = []
                try:
                    dig = int(tok[word_mark].text.split(split_t)[0].replace(',', ''))
                    mult_rpm.append(dig)
                    spin_mark.append(word_mark)
                    n = 2
                    while True:
                        if tok[word_mark - n].text != 'and' and tok[word_mark - n].text != ',':
                            break
                        try:
                            dig = int(tok[word_mark - n - 1].text.replace(',', ''))
                            mult_rpm.append(dig)
                            multiple = 1
                        except:
                            pass
                        n += 2
                except:
                    pass
                for ids in range(len(mult_rpm)):
                    spin_coat[0].append(mult_rpm[len(mult_rpm)-1-ids])
                # print(spin_coat)
            for unit in spin_coating_unit:
                mult_time = []
                if tok[word_mark].text == unit:
                    try:
                        dig = int(tok[word_mark - 1].text.replace(',', ''))
                        boo = 0
                        if spin_mark != []:
                            for m in spin_mark:
                                if word_mark < m + 11 and word_mark > m - 11:
                                    boo = 1
                        if boo == 1:
                            mult_time.append(unit)
                            mult_time.append(dig)
                            n = 2
                            while True:
                                if tok[word_mark - n].text != 'and' and tok[word_mark - n].text != ',':
                                    break
                                try:
                                    dig = int(tok[word_mark - n - 1].text.replace(',', ''))
                                    mult_time.append(unit)
                                    mult_time.append(dig)
                                except:
                                    pass
                                n += 2
                    except:
                        pass
                elif unit in tok[word_mark].text.replace(',', ''):
                    try:
                        dig2 = int(tok[word_mark].text.replace(',', '').split(unit)[0])
                        boo = 0
                        if spin_mark != []:
                            for m in spin_mark:
                                if word_mark < m + 6 and word_mark > m - 6:
                                    boo = 1
                        if boo == 1:
                            mult_time.append(unit)
                            mult_time.append(dig)
                            n = 2
                            while True:
                                if tok[word_mark - n].text != 'and' or tok[word_mark - n].text != ',':
                                    break
                                try:
                                    if multiple == 1:
                                        dig2 = int(tok[word_mark - n - 1].text.replace(',', ''))
                                        mult_time.append(unit)
                                        mult_time.append(dig)
                                        # spin_coat[1].append(dig2)
                                        # spin_coat[1].append(unit)
                                    n += 2
                                except:
                                    pass
                    except:
                        pass

                for ids in range(len(mult_time)):
                    spin_coat[1].append(mult_time[len(mult_time)-1-ids])
            for m in material_list:
                if m.lower() == tok[word_mark].text.lower(): # todo what if material is 2 words
                    spin_coat[2].append(m)
                    if on_mark[0] != 0:
                        if word_mark > on_mark[0] and ((on_mark[1] != 0 and word_mark < on_mark[1]) or word_mark < on_mark[0] + 5):
                            spin_coat[3].append(m)
        # print(sen.text)
        # print(final_spin_coat)
        if spin_coat != [[], [], [], []]:
            final_spin_coat = spin_coat
    return final_spin_coat

def anneal_mining(sen):
    final_ann = []
    ann = [[], []]    # temp, duration
    if 'anneal' in sen.text or 'hotplate' in sen.text or 'heat' in sen.text:
        tok = sen.tokens
        ann_mark = []
        for word_mark in range(len(tok)):
            if 'C' == tok[word_mark].text.replace('(', '').replace(')', '').replace(',', '') \
                    and '°' == tok[word_mark-1].text.replace('(', '').replace(')', '').replace(',', ''):
                temp_predict = tok[word_mark-2].text.replace('(', '').replace(')', '').replace(',', '')
                try:
                    dig = int(temp_predict)
                    ann[0].append(dig)
                    ann_mark.append(word_mark)
                except:
                    pass
            elif '∘C' == tok[word_mark].text.replace('(', '').replace(')', '').replace(',', ''):
                temp_predict = tok[word_mark-1].text.replace('(', '').replace(')', '').replace(',', '')
                try:
                    dig = int(temp_predict)
                    ann[0].append(dig)
                    ann_mark.append(word_mark)
                except:
                    pass
            else:
                ann_unit = ['s', 'min', 'h', 'seconds', 'minutes']
                for unit in ann_unit:
                    if tok[word_mark].text.replace('(', '').replace(')', '').replace(',', '') == unit:
                        try:
                            dig = int(tok[word_mark - 1].text.replace('(', '').replace(')', '').replace(',', ''))
                            boo = 0
                            if ann_mark != []:
                                for m in ann_mark:
                                    if word_mark < m + 6 and word_mark > m - 6:
                                        boo = 1
                            if boo == 1:
                                ann[1].append(dig)
                                ann[1].append(unit)
                        except:
                            pass
                    elif unit in tok[word_mark].text.replace('(', '').replace(')', '').replace(',', ''):
                        try:
                            dig2 = int(tok[word_mark].text.replace('(', '').replace(')', '').replace(',', '').split(unit)[0])
                            boo = 0
                            if ann_mark != []:
                                for m in ann_mark:
                                    if word_mark < m + 6 and word_mark > m - 6:
                                        boo = 1
                            if boo == 1:
                                ann[1].append(dig2)
                                ann[1].append(unit)
                        except:
                            pass
        if ann != [[], []]:
            final_ann = ann
    return final_ann
