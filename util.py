#helper functions
from flask import Markup
import connection
import data_manager
import datetime
import bcrypt



def hash_pw(password):
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed_bytes_password)

def verify_username(username):
    list_of_usernames_in_db = data_manager.get_list_of_values_for_column_in_db_table('username','users')
    if username in list_of_usernames_in_db:
        return True
    else:
        return False

def verify_login(username,password):
    if verify_username(username):
        user_row = connection.get_data_by_value_pair_from_table({'username': username}, 'users')[0]
        hashed_password = user_row['password']
        is_a_match = verify_password(password,hashed_password)
        return is_a_match
    else:
        return False

def embed_substring_in_CSS_class(substring: str):
    return lambda full_string: Markup(full_string.replace(
        substring, 
        '<u class=c-search-phrase>'+substring+'</u>'
    ))  # is this a safe thing to do? Markup marks the object as safe for Flask rendering of Jinja.

def perform_search_logic(search_string):
    asMarkup_search_phrase = embed_substring_in_CSS_class(search_string)
    matched_question_ids = []
    matched_in_all_qids = data_manager.find_pattern_in_question_title_message_and_answer_message(
        given_pattern=search_string
    )
    db_modified_questions = []
    for question_id in matched_in_all_qids:
        matched_question_ids.append(question_id)
        question_dict = data_manager.get_from_table_by_id(question_id, 'question')     
        question_dict['title'] = asMarkup_search_phrase(question_dict['title'])
        question_dict['message'] = asMarkup_search_phrase(question_dict['message'])
        # print("Title: ", question_dict['title'])
        # print("Message: ", question_dict['message'])                
        list_of_answers = data_manager.magic_answer_get(question_id)
        answers_to_display = []
        for answer in list_of_answers:
            if search_string in answer['message']:
                answer['message'] = asMarkup_search_phrase(answer['message'])
                answers_to_display.append(answer)
                # print('Answer ',answer['id'],": ", answer['message'])
        question_dict['answer_list'] = answers_to_display
        db_modified_questions.append(question_dict)
    
    return db_modified_questions
        

def convert_time_to_str(date_time_obj: datetime.datetime):
    try:
        time_str = date_time_obj.strftime('%Y-%m-%d %H:%M:%S')+" (UTC)"
    except (TypeError, ValueError):
        time_str = "..."

    return time_str


def make_str_as_int_or_zero(some_str):
    try:
        my_int = int(some_str)
    except (TypeError, ValueError):
        my_int = 0  # reset the number if it's stored as a malformed string    
    return my_int





if __name__ == "__main__":
    perform_search_logic('ing')



