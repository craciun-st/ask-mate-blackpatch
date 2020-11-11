import connection

def get_all_rows_from_table(table_name: str):
    list_of_dict = connection.get_data_from_table(table_name)
    return list_of_dict


def get_questions():
    
    list_of_questions = connection.get_data_from_table('question')
    return list_of_questions

def get_answers():
    list_of_answers = connection.get_data_from_table('answer')
    return list_of_answers


def get_from_table_by_id(id_val,table_name):
    try:
        new_id_val = int(id_val)
    except (TypeError, ValueError):
        print('Wrong kind of id given!')
        return {}
    result_dict = connection.get_data_by_value_pair_from_table({'id': new_id_val}, table_name)[0]
    return result_dict


def get_comments_from_answer_id(answer_id_val):
    return connection.get_sorted_inner_join_between_tables_where_table2_column_has_value_and_order_by_table1_column(
        table1_name='comment',
        table1_keycol='answer_id',        
        table2_name='answer',
        table2_keycol='id',
        table2_column='id',
        table2_column_value=answer_id_val,
        table1_column_to_order='submission_time',
        reverse=True
    )

def get_username_from_answer_id(answer_id_val):
    answer_row = connection.get_data_by_value_pair_from_table(
        {'id': answer_id_val}, 'answer'
    )[0]
    user_id_value = answer_row['user_id']

    if user_id_value:
        user_row = connection.get_data_by_value_pair_from_table(
            {'id': user_id_value}, 'users'
        )[0]
        username = user_row['username']
        return username
    else:
        return "Anonymous"

def get_username_from_question_id(question_id_val):
    question_row = connection.get_data_by_value_pair_from_table(
        {'id': question_id_val}, 'question'
    )[0]
    user_id_value = question_row['user_id']

    if user_id_value:
        user_row = connection.get_data_by_value_pair_from_table(
            {'id': user_id_value}, 'users'
        )[0]
        username = user_row['username']
        return username
    else:
        return "Anonymous"

# #----------username for question comment----------
# def get_username_from_comment_question_id(question_id_val):
#     comment_row = connection.get_data_by_value_pair_from_table(
#         {'question_id': id}, 'comment'
#     )[0]
#     user_id_value = comment_row['user_id']

#     if user_id_value:
#         user_row = connection.get_data_by_value_pair_from_table(
#             {'id': user_id_value}, 'users'
#         )[0]
#         username = user_row['username']
#         return username
#     else:
#         return "Anonymous"
# #--------------------------------------------------
#----------username for answer comment----------
def get_username_from_user_id(user_id_value):

    if user_id_value:
        user_row = connection.get_data_by_value_pair_from_table(
            {'id': user_id_value}, 'users'
        )[0]
        username = user_row['username']
        return username
    else:
        return "Anonymous"
#--------------------------------------------------

def get_tags_for_question_id(question_id_val):
    return connection.get_sorted_inner_join_between_tables_where_table2_column_has_value_and_order_by_table1_column(
        table1_name='tag',
        table1_keycol='id',        
        table2_name='question_tag',
        table2_keycol='tag_id',
        table2_column='question_id',
        table2_column_value=question_id_val,
        table1_column_to_order='id',
        reverse=True
    )

def get_multiple_rows_from_table_by_name(name,table_name):
    result_dict = connection.get_data_by_value_pair_from_table({'name': name}, table_name)
    return result_dict

def get_multiple_rows_for_question_id(question_id,table_name):
    result_dict = connection.get_data_by_value_pair_from_table({'question_id':question_id}, table_name)
    return result_dict


def get_multiple_rows_for_answer_id(answer_id,table_name):
    result_dict = connection.get_data_by_value_pair_from_table({'answer_id':answer_id}, table_name)
    return result_dict


def get_question_id_from_answer_id(answer_id_val):
    answer = get_from_table_by_id(answer_id_val, 'answer')
    return answer['question_id']


def get_list_of_values_for_question_field(list_of_dict, field: str):
    my_list = []
    if field in connection.column_names_dict['question']:
        for row in list_of_dict:
            my_list.append(row[field])
            
    return my_list


def get_sorted_all_rows_from_table_by_column(table_name, column_to_order_by, reverse=False):
    return connection.get_sorted_all_rows_from_table_order_by(table_name, column_to_order_by, reverse)

def magic_answer_get(question_id_val):

    return connection.get_sorted_inner_join_between_tables_where_table2_column_has_value_and_order_by_table1_column(
        table1_name='answer',
        table2_name='question',    
        table2_column='id',
        table2_column_value=question_id_val,
        table1_keycol='question_id',
        table2_keycol='id',    
        table1_column_to_order='vote_number',
        reverse=True
    )


def append_new_row_in_table(some_dict, table_name):
    connection.append_row_in_table(some_dict, table_name)


#general for write
def write_modified_row_in_table(some_dict, table_name, id_val=None):
    connection.update_data_in_table(some_dict, table_name, id_val)

def delete_row(id_val,table_name):
    connection.delete_data(id_val,table_name)


def delete_tag(id_val,table_name,tag_id_value):
    connection.delete_tag_by_question_id(id_val,table_name,tag_id_value)


def find_pattern_in_question_title_message_and_answer_message(given_pattern: str):
    list_of_dict = connection.search_pattern_in_triplet_intersect(
        table_list=['question', 'question', 'answer'],
        search_column_list=['title', 'message', 'message'],
        union_column_list=['id','id','question_id'],
        pattern_str=given_pattern
    )
    id_list=[row['id'] for row in list_of_dict]
    return id_list