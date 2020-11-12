from flask import Flask, request, render_template, redirect, url_for, send_from_directory, session

import data_manager
import connection
import os
import util


app = Flask(__name__)
app.secret_key = 'aperughpearuhg-0934q=-9343=q45w6y954=45qw=hg94'

app.config['UPLOAD_FOLDER'] = "./images"
ALLOWED_EXTENSIONS = {'png', 'jpeg', 'jpg'}

int_question_fields = ['view_number', 'vote_number']


def allowed_file(filename: str):  # filtering the allowed files

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/images/<filename>')
def get_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route("/")
def main_page():
    if 'username' in session:
        is_logged_in = True
    else:
        is_logged_in = False
    return render_template('index.html', is_logged_in = is_logged_in)

@app.route("/login", methods = ['POST','GET'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if util.verify_login(username,password) == True:
            session['username'] = username
            return redirect('/')
        else:
            return render_template('login.html', correct_credentials = False)

    return render_template('login.html', correct_credentials = True)

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route("/registration", methods = ['POST','GET'])
def registration_page():
    if request.method == 'POST':
        posted_data = request.form
        is_already_used = util.verify_username(posted_data['username'])
        if is_already_used == False:
            data_manager.filling_missing_fields_user(posted_data)
            return redirect("/")
        else:
            return render_template('registration.html', correct_credentials = False)
    return render_template('registration.html', correct_credentials = True)

@app.route("/users")
def users_page():
    users_db = data_manager.get_all_rows_from_table('users')
    return render_template('users.html', users_db=users_db)

@app.route("/tags")
def tags_page():
    all_tags = data_manager.get_tagnames_sorted_by_use_count_in_questions()
    return render_template("tags.html", tag_list=all_tags)



@app.route('/list')
def listing():
    if 'username' in session:
        is_logged_in = True
    else:
        is_logged_in = False
    sort_by = request.args["sort-by"] if 'sort-by' in request.args.keys() else "submission_time"
    sort_order = request.args["sort-order"] if 'sort-order' in request.args.keys() else "true"
    is_descending = (sort_order.lower() in ['true', 't', 'yes'])

    questions = data_manager.get_sorted_all_rows_from_table_by_column(
        table_name='question',
        column_to_order_by=sort_by,
        reverse=is_descending
    )
    questions = data_manager.update_dict_with_utctime_str(questions)
    

    return render_template('list.html', db_questions=questions, is_logged_in = is_logged_in)


@app.route('/question/<question_id>')
# route that displays the question with the specified ID and the answers for that question
def question(question_id):
    if 'username' in session:
        is_logged_in = True
    else:
        is_logged_in = False
    question_comments = data_manager.get_multiple_rows_for_question_id(
        question_id, 'comment')
    question_tags =data_manager.get_tags_for_question_id(question_id)
    question_comments = data_manager.update_dict_with_utctime_str(question_comments)

    for this_question_comment in question_comments:
        current_user = data_manager.get_username_from_user_id(this_question_comment['user_id'])
        this_question_comment.update({'username': current_user})

    answers = data_manager.magic_answer_get(int(question_id))
    if len(answers) > 0:

        for answer in answers:
            curr_comments = data_manager.get_comments_from_answer_id(
                answer['id'])
            curr_comments = data_manager.update_dict_with_utctime_str(curr_comments)

            for this_answer_comment in curr_comments:
                current_user = data_manager.get_username_from_user_id(this_answer_comment['user_id'])
                this_answer_comment.update({'username': current_user})

            current_user = data_manager.get_username_from_answer_id(answer['id'])
            answer.update({"comment_list": curr_comments})
            answer.update({"username": current_user})


    question = data_manager.get_from_table_by_id(int(question_id), 'question')

    # TODO: write 400 route for id not in DB (found_id = False)
    found_id = True
    try:
        view_nr = int(question['view_number'])
    except (ValueError, TypeError):
        view_nr = 0
    view_nr += 1
    question['view_number'] = str(view_nr)

    question_user = data_manager.get_username_from_question_id(question_id)
    question['username'] = question_user

    # for sorting by votes  :D python style, in case sql doesn't work
    #answers = sorted(answers, key=lambda row:int(row['vote_number']), reverse= False)

    if found_id:
        data_manager.write_modified_row_in_table(question, 'question')

        return render_template('question.html', input_id=question_id,
                               question=question,
                               corresponding_answers=answers,
                               comments_for_question=question_comments,
                               question_tags = question_tags,
                               is_logged_in = is_logged_in
                               )
    else:
        return "Could not find such a question!", 400


@app.route('/add-question', methods=["GET"])
def display_new_question():
    global session
    if 'username' in session:
        is_logged_in = True
    else:
        is_logged_in = False
        return render_template('not_authenticated.html'), 401
    return render_template('add-question.html')


@app.route('/add-question', methods=["POST"])
def update_with_new_question():

    posted_data = request.form

    
    have_to_write_image = False
    # uploading a file
    img_file_object = request.files['file']
    if img_file_object and allowed_file(img_file_object.filename):

        #TODO Refactor image uploading logic in util/data_manager           #
        have_to_write_image = True                                          #
        my_path_name = os.path.join(                                        #
            app.config['UPLOAD_FOLDER'], img_file_object.filename)          #
        img_file_object.save(my_path_name)                                  #

    question_dict = data_manager.fill_missing_fields_question(posted_data)  
    # checking that there is a file
    if have_to_write_image:
        # HTML can not find the file if we don't get rid of the '.' at the start of the path
        question_dict.update({'image': my_path_name[1:]})
    
    #testing---------------------
    session = {'user_id': 3}
    question_dict.update({'user_id': session['user_id']})
    #----------------------------

    data_manager.append_new_row_in_table(question_dict, 'question')
    return redirect("/question/"+str(question_dict["id"]))


@app.route('/question/<question_id>/vote_up', methods=["GET", "POST"])
# a button for voting up, it adds up our votes and writes it in our data base
def vote_up(question_id):
    #
    question = data_manager.get_from_table_by_id(question_id, 'question')
    question_author = data_manager.get_author_from_question_id(question_id)
    vote_nr = util.make_str_as_int_or_zero(question['vote_number'])
    author_rep = util.make_str_as_int_or_zero(question_author['reputation'])

    vote_nr += 1
    author_rep += 5
    
    question['vote_number'] = vote_nr
    question_author['reputation'] = author_rep
    data_manager.write_modified_row_in_table(question, 'question')
    data_manager.write_modified_row_in_table(question_author, 'users')
    return redirect("/list")


@app.route('/question/<question_id>/vote_down')
def vote_down(question_id):
    # a button for voting down, it substracts our votes and writes it in our data base
    question = data_manager.get_from_table_by_id(question_id, 'question')
    question_author = data_manager.get_author_from_question_id(question_id)
    vote_nr = util.make_str_as_int_or_zero(question['vote_number'])
    author_rep = util.make_str_as_int_or_zero(question_author['reputation'])

    vote_nr -= 1
    author_rep -= 2
    
    question['vote_number'] = vote_nr
    question_author['reputation'] = author_rep
    data_manager.write_modified_row_in_table(question, 'question')
    data_manager.write_modified_row_in_table(question_author, 'users')
    return redirect("/list")


@app.route('/question/<question_id>/new-answer', methods=['POST', 'GET'])
def answer(question_id):
    global session
    if 'username' in session:
        is_logged_in = True
    else:
        is_logged_in = False
        return render_template('not_authenticated.html'), 401
    # route for the answer page, adds an answer to a question with a specified ID when called with POST method, calling this route with GET methon will render our add-answer template
    if request.method == 'POST':
        have_to_write_image = False
        # uploading a file
        img_file_object = request.files['file']
        if img_file_object and allowed_file(img_file_object.filename):
            have_to_write_image = True
            my_path_name = os.path.join(
                app.config['UPLOAD_FOLDER'], img_file_object.filename)
            img_file_object.save(my_path_name)
        posted_data = request.form
        answer_dict = data_manager.fill_missing_fields_answer(posted_data)
        answer_dict.update({'question_id': question_id})
        #for testing purposes
        session = {'user_id' : 2}
        answer_dict.update({'user_id': session['user_id']}) 
        # checking that there is a file
        if have_to_write_image:
            # my_path_name= os.path.join(my_path_name, '_'+str(answer_dict['id'])
            # HTML can not find the file if we don't get rid of the '.' at the start of the path
            answer_dict.update({'image': my_path_name[1:]})
        data_manager.append_new_row_in_table(answer_dict, 'answer')
        return redirect("/question/" + question_id)
    elif request.method == 'GET':
        return render_template('add-answer.html', input_id=question_id)


@app.route('/answer/<answer_id>/vote_up')
def vote_up_answer(answer_id):
    answer = data_manager.get_from_table_by_id(answer_id, 'answer')
    answer_author = data_manager.get_author_from_answer_id(answer_id)
    question_id_as_str = str(answer['question_id'])        
    vote_nr = util.make_str_as_int_or_zero(answer['vote_number'])
    author_rep = answer_author['reputation']
    
    vote_nr += 1
    author_rep += 10
    
    answer['vote_number'] = vote_nr
    answer_author['reputation'] = author_rep
    data_manager.write_modified_row_in_table(answer, 'answer')
    data_manager.write_modified_row_in_table(answer_author, 'users')
    return redirect("/question/" + question_id_as_str)


@app.route('/answer/<answer_id>/vote_down')
def vote_down_answer(answer_id):
    answer = data_manager.get_from_table_by_id(answer_id, 'answer')
    answer_author = data_manager.get_author_from_answer_id(answer_id)
    question_id_as_str = str(answer['question_id'])        
    vote_nr = util.make_str_as_int_or_zero(answer['vote_number'])
    author_rep = answer_author['reputation']
    
    vote_nr -= 1
    author_rep -= 2
    
    answer['vote_number'] = vote_nr
    answer_author['reputation'] = author_rep
    data_manager.write_modified_row_in_table(answer, 'answer')
    data_manager.write_modified_row_in_table(answer_author, 'users')
    return redirect("/question/" + question_id_as_str)


@app.route('/question/<question_id>/delete')
# a route that deletes dictionaries (quesiton and answers) from our list and then writes the new list into the data base
def delete_question(question_id):
    question = data_manager.get_from_table_by_id(question_id, 'question')
    answers = data_manager.get_multiple_rows_for_question_id(
        question_id, 'answer')
    if question['image']:
        os.remove('.'+str(question['image']))
    for row in answers:
        if row['image']:
            os.remove('.'+str(row['image']))
    data_manager.delete_row(question_id, 'question')
    return redirect('/list')


@app.route('/question/<question_id>/edit', methods=["GET"])
def show_question_edit(question_id):
    question = data_manager.get_from_table_by_id(question_id, 'question')
    return render_template("edit-question.html", input_question=question)
    # if found_id:
    #     return render_template("edit-question.html", input_question = specific_question)
    # else:
    #     return "Could not find such a question!", 400


@app.route('/question/<question_id>/edit', methods=["POST"])
def do_question_edit(question_id):
    # it's OK if question_id is a string repr. a number
    question = data_manager.get_from_table_by_id(question_id, 'question')
    posted_data = request.form
    for field in connection.column_names_dict['question']:
        if field in posted_data:
            question.update({field: posted_data[field]})
    data_manager.write_modified_row_in_table(question, 'question')
    return redirect("/question/"+question_id)


@app.route('/question/<question_id>/new-tag', methods=["GET", "POST"])
def new_tag_route(question_id):
    if request.method == "POST":
        tags_data = request.form
        tag_name = tags_data["tagname"]
        all_tag_rows = data_manager.get_all_rows_from_table('tag')
        # [ {'id': 1, 'name': 'css'},  {'id': 2, 'name': 'sql'} ... ]
        list_of_tag_names = data_manager.get_list_of_values_for_column_in_py_table_list(
            all_tag_rows,
            'name',
            'tag'
        )
        # ['css', 'sql', ...]

        if tag_name not in list_of_tag_names:
            tag_dict = data_manager.fill_missing_fields_from_table({'name':tag_name}, 'tag')
            tag_id = tag_dict['id']
            data_manager.append_new_row_in_table(tag_dict , 'tag')
            data_manager.append_new_row_in_table({'tag_id':tag_id, 'question_id':question_id}, 'question_tag')
        else:
            tag_dict= data_manager.get_multiple_rows_from_table_by_name(tag_name,'tag')[0]
            tag_id = tag_dict['id']
            data_manager.append_new_row_in_table({'tag_id':tag_id, 'question_id':question_id}, 'question_tag')
        return redirect("/question/"+question_id)



@app.route('/question/<question_id>/tag/<tag_id>/delete', methods= ["GET","POST"])
def delete_tags(question_id,tag_id):
    data_manager.delete_tag(
        id_val=question_id,
        tag_id_value=tag_id,
        table_name='question_tag')
    return redirect('/question/'+ str(question_id))
    


@app.route('/question/<question_id>/new-comment', methods=['POST', 'GET'])
def new_comment_question(question_id):
    if request.method == 'POST':
        posted_data = request.form
        comment_dict = data_manager.fill_missing_fields_from_table(
            posted_data, 'comment')
        comment_dict.update({'question_id': question_id})
        #---test-------
        session = {'user_id' : 4}
        comment_dict.update({'user_id': session['user_id']})
        #-----------
        data_manager.append_new_row_in_table(comment_dict, 'comment')
        return redirect('/question/' + question_id)


@app.route('/answer/<answer_id>/new-comment', methods=['POST'])
def new_comment_answer(answer_id):
    answer = data_manager.get_from_table_by_id(answer_id, 'answer')
    question_id_as_str = str(answer['question_id'])
    if request.method == 'POST':
        posted_data = request.form
        comment_dict = data_manager.fill_missing_fields_from_table(
            posted_data, 'comment')
        comment_dict.update({'answer_id': answer_id})
        #---test-------
        session = {'user_id' : 4}
        comment_dict.update({'user_id': session['user_id']})
        #-----------
        data_manager.append_new_row_in_table(comment_dict, 'comment')
        return redirect('/question/' + question_id_as_str)


@app.route('/comment/<comment_id>/delete')
def delete_comment(comment_id):
    comment = data_manager.get_from_table_by_id(comment_id, 'comment')
    if comment['answer_id']:
        return_question_id = data_manager.get_question_id_from_answer_id(
            comment['answer_id'])
    elif comment['question_id']:
        return_question_id = comment['question_id']
    else:
        return "Wrong comment id", 400
    data_manager.delete_row(comment_id, 'comment')
    return redirect('/question/' + str(return_question_id))


@app.route('/comment/<comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    comment = data_manager.get_from_table_by_id(comment_id, 'comment')
    if comment['answer_id']:
        return_question_id = data_manager.get_question_id_from_answer_id(
            comment['answer_id'])
    elif comment['question_id']:
        return_question_id = comment['question_id']
    if request.method == 'GET':
        return render_template('edit-comment.html', input_comment=comment)
    else:
        posted_data = request.form
        for field in connection.column_names_dict['comment']:
            if field in posted_data:
                comment.update({field: posted_data[field]})
        data_manager.write_modified_row_in_table(comment, 'comment')
    return redirect('/question/'+str(return_question_id))


@app.route('/search', methods=['GET', 'POST'])
def display_search_results():
    if request.method == 'GET':         
        search_string = request.args.get('q')
        if len(search_string) < 3:
            return redirect("/list")
        else:            
            db_modified_questions = util.perform_search_logic(search_string)

            return render_template("search_results.html", db_questions=db_modified_questions)


if __name__ == "__main__":    
    app.run(debug=True)
