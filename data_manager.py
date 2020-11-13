from data_manager_specific_cases import *
import connection
from connection import magic_get_users_hardcoded_labels
import datetime
import csv
import util




def get_multiple_rows_from_table_by_id(id_val,table_name):
    try:
        new_id_val = int(id_val)
    except (TypeError, ValueError):
        print('Wrong kind of id given!')
        return {}
    result_dict = connection.get_data_by_value_pair_from_table({'id': new_id_val}, table_name)
    return result_dict





# SQL logic
def get_list_of_values_for_column_in_db_table(column_name: str, table_name):
    # special case for just one column!
    if column_name in connection.column_names_dict[table_name]:
        my_list_of_dict = connection.get_specific_columns_from_table([column_name], table_name)

    value_list = [row[column_name] for row in my_list_of_dict]    
            
    return value_list  # it is natural to return just a list of values, rather than a list of dictionaries


# Python logic
def get_list_of_values_for_column_in_py_table_list(list_of_dict, column_name: str, table_name):
    my_list = []
    if column_name in connection.column_names_dict[table_name]:
        for row in list_of_dict:
            my_list.append(row[column_name])
            
    return my_list


  


def fill_missing_fields_question(partial_dict, file_path=None):
#uses list of headers for fields and iterates through it, adding the field as a key and the corresponding value from the partial dictionary
    question_dict = {}
    for field in connection.column_names_dict['question']:
        if field in partial_dict:
            question_dict.update({field: partial_dict[field]})
        else:
            if field == "id":
                new_id = connection.get_max_serial_from_table('question') + 1
                question_dict.update({'id': new_id})
            # -----------user_id--------------------------------
            elif field == "user_id":
                new_user_id = None
                question_dict.update({'user_id': new_user_id})
            # --------------------------------------------
            elif field == "submission_time":
                curr_time = datetime.datetime.utcnow()                
                question_dict.update({"submission_time": curr_time})
            elif field == "image":
                if file_path != None:
                    question_dict.update({field: file_path})
            else:
                question_dict.update({field:0})
    return question_dict


def fill_missing_fields_answer(partial_dict, file_path=None):
    answer_dict = {}
    for field in connection.column_names_dict['answer']:
        if field in partial_dict:
            answer_dict.update({field : partial_dict[field]})
        else:
            if field == "id":
                new_id = connection.get_max_serial_from_table('answer') + 1
                answer_dict.update({'id': new_id})
                # -----------user_id--------------------------------
            elif field == "user_id":
                new_user_id = None
                answer_dict.update({'user_id': new_user_id})
                # --------------------------------------------
            elif field == 'submission_time':
                current_time = datetime.datetime.utcnow()                
                answer_dict.update({'submission_time' : current_time})
            elif field == "image":
                if file_path != None:
                    answer_dict.update({field: file_path})
            else:
                answer_dict.update({field:0})
    return answer_dict

def filling_missing_fields_user(partial_dict,):
    user_dict = {}
    for field in connection.column_names_dict['users']:
        if field in partial_dict:
            
            if field == 'password':
                hashed_pw = util.hash_pw(partial_dict['password'])
                user_dict.update({'password':hashed_pw})
            else:
                user_dict.update({field:partial_dict[field]})

        else:
            if field == "id":
                new_id = connection.get_max_serial_from_table('users') + 1
                user_dict.update({'id':new_id})
            elif field == 'date_of_registration':
                current_time = datetime.datetime.utcnow()
                user_dict.update({"date_of_registration": current_time})            
            elif field == 'reputation':
                user_dict.update({'reputation': 0})
    append_new_row_in_table(user_dict, 'users')

def fill_missing_fields_from_table(partial_dict,table_name, file_path=None):
    used_dict = {}
    for field in connection.column_names_dict[table_name]:
        if field in partial_dict:
            used_dict.update({field : partial_dict[field]})
        else:
            if field == "id":
                new_id = connection.get_max_serial_from_table(table_name) + 1
                used_dict.update({'id': new_id})
            elif field == 'submission_time':
                current_time = datetime.datetime.utcnow()                
                used_dict.update({'submission_time' : current_time})
            elif field in ['question_id', 'answer_id']:
                pass
            else:
                used_dict.update({field:0})
    return used_dict



def update_dicts_with_utctime_str(my_dict_list):
    for i in range(len(my_dict_list)):
        if 'submission_time' in my_dict_list[i]:
            time_str_for_this_row = util.convert_time_to_str(
                my_dict_list[i]['submission_time'])
            my_dict_list[i].update({'utctime_str': time_str_for_this_row})
        if 'date_of_registration' in my_dict_list[i]:
            time_str_for_this_row = util.convert_time_to_str(
                my_dict_list[i]['date_of_registration'])
            my_dict_list[i].update({'date_of_reg_utc': time_str_for_this_row})

    return my_dict_list

    