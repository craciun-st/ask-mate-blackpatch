#the connection between database and our server

import os   # to get environment variables
import psycopg2  # you know what this is!
from psycopg2 import sql  # allows us to build up SQL compositions of identifier/literals
                          # needed for security reasons (protect against SQL injection)

from psycopg2.extras import RealDictCursor  # import the type RealDictCursor
from connection_wrapper import connection_handler
import datetime


@connection_handler
def get_column_names_from_table(cursor: RealDictCursor, table_name):
    query=sql.SQL("""
        SELECT * FROM {sql_table_name}
    """).format(sql_table_name= sql.Identifier(table_name))
    cursor.execute(query)
    simple_dict = cursor.fetchone()
    table_fields = [key for key in simple_dict]
    return table_fields

# This dictionary is used by data_manager
column_names_dict={}
for table_name in ['question', 'answer', 'comment', 'tag', 'question_tag', 'users']:
    column_names_dict.update({ table_name : get_column_names_from_table(table_name) })


@connection_handler
def get_data_from_table(cursor: RealDictCursor, table_name):
    query= sql.SQL('''
        SELECT * FROM {sql_table_name}
    ''').format(sql_table_name=sql.Identifier(table_name))
    cursor.execute(query)
    result_rows = cursor.fetchall()
    
    return result_rows


@connection_handler
def get_specific_columns_from_table(cursor: RealDictCursor, column_name_list, table_name):
    table_fields = column_names_dict[table_name]
    intersection_fields = [field for field in table_fields if field in column_name_list]    

    joined_sql_column_names = sql.SQL(', ').join( sql.Identifier(n) for n in intersection_fields )

    query= sql.SQL('''
        SELECT {sql_column_list} FROM {sql_table_name}
    ''').format(
        sql_table_name=sql.Identifier(table_name),
        sql_column_list=joined_sql_column_names
        )
    cursor.execute(query)
    result_rows = cursor.fetchall()


@connection_handler
def get_table1_column_from_inner_join_between_tables_where_table2_column_has_value(
    cursor: RealDictCursor,
    table1_name,
    table2_name,    
    table1_column,
    table2_column,
    table2_column_value,
    table1_keycol,
    table2_keycol,    
):
    list1 = [table1_name, table1_keycol]
    list2 = [table2_name, table2_keycol]
    keystring_t1 = sql.SQL('.').join(sql.Identifier(n) for n in list1)
    keystring_t2 = sql.SQL('.').join(sql.Identifier(n) for n in list2) 
    query=sql.SQL("""
        SELECT {sql_table1_name}.{sql_table1_column} FROM {sql_table1_name} INNER JOIN {sql_table2_name}
            ON {sql_keystring_t1} = {sql_keystring_t2}
        WHERE {sql_table2_name}.{sql_table2_column} = %(table2_value)s        
    """).format(
        sql_table1_name = sql.Identifier(table1_name),
        sql_table2_name = sql.Identifier(table2_name),
        sql_keystring_t1 = keystring_t1,
        sql_keystring_t2 = keystring_t2,
        sql_table2_column = sql.Identifier(table2_column),
        sql_table1_column = sql.Identifier(table1_column)        
        )
    cursor.execute(query, {"table2_value": table2_column_value})
    result_rows = cursor.fetchall()

    return result_rows


@connection_handler
def get_sorted_inner_join_between_tables_where_table2_column_has_value_and_order_by_table1_column(
    cursor: RealDictCursor,
    table1_name,
    table2_name,    
    table2_column,
    table2_column_value,
    table1_keycol,
    table2_keycol,    
    table1_column_to_order,
    reverse=False
):
    list1 = [table1_name, table1_keycol]
    list2 = [table2_name, table2_keycol]    
    list3 = [table1_name, table1_column_to_order]
    keystring_t1 = sql.SQL('.').join(sql.Identifier(n) for n in list1)
    keystring_t2 = sql.SQL('.').join(sql.Identifier(n) for n in list2)
    column_string_t1 = sql.SQL('.').join(sql.Identifier(n) for n in list3)
    if reverse:
        query=sql.SQL("""
            SELECT {sql_table1_name}.* FROM {sql_table1_name} INNER JOIN {sql_table2_name}
                ON {sql_keystring_t1} = {sql_keystring_t2}
            WHERE {sql_table2_name}.{sql_table2_column} = %(table2_value)s
            ORDER BY {sql_column_string_t1} DESC
        """).format(
            sql_table1_name = sql.Identifier(table1_name),
            sql_table2_name = sql.Identifier(table2_name),
            sql_keystring_t1 = keystring_t1,
            sql_keystring_t2 = keystring_t2,
            sql_table2_column = sql.Identifier(table2_column),
            sql_column_string_t1 = column_string_t1
            )
    else:
       query=sql.SQL("""
            SELECT {sql_table1_name}.* FROM {sql_table1_name} INNER JOIN {sql_table2_name}
                ON {sql_keystring_t1} = {sql_keystring_t2}
            WHERE {sql_table2_column} = %(table2_value)s
            ORDER BY {sql_column_string_t1} DESC
        """).format(
            sql_table1_name = sql.Identifier(table1_name),
            sql_table2_name = sql.Identifier(table2_name),
            sql_keystring_t1 = keystring_t1,
            sql_keystring_t2 = keystring_t2,
            sql_table2_column = sql.Identifier(table2_column),
            sql_column_string_t1 = column_string_t1
            )
    cursor.execute(query, {"table2_value": table2_column_value})
    result_rows = cursor.fetchall()

    return result_rows


@connection_handler
def get_max_serial_from_table(cursor: RealDictCursor, table_name):
    query=sql.SQL("""
        SELECT max({sql_id}) FROM {sql_table_name}
    """
    ).format(
        sql_id = sql.Identifier('id'),
        sql_table_name = sql.Identifier(table_name)
        )
    cursor.execute(query)
    result_dict = cursor.fetchone()
    return int(result_dict['max'])


@connection_handler
def get_data_by_value_pair_from_table(cursor: RealDictCursor, field_dict, table_name):
    column_name = [key for key in field_dict][0]
    column_value = field_dict[column_name]
    query=sql.SQL("""
        SELECT * FROM {sql_table_name} 
        WHERE {sql_column_name} = %(column_val)s
    """).format(
        sql_table_name = sql.Identifier(table_name),
        sql_column_name = sql.Identifier(column_name)
        )
    cursor.execute(query,{"column_val": column_value})
    result_rows = cursor.fetchall()

    return result_rows


@connection_handler
def get_sorted_all_rows_from_table_order_by(cursor: RealDictCursor, table_name, column_name, reverse=False):
    if reverse :
        query=sql.SQL("""
            SELECT * FROM {sql_table_name} ORDER BY {sql_column_name} DESC
        """).format(
            sql_table_name = sql.Identifier(table_name),
            sql_column_name = sql.Identifier(column_name)
            )
    else:
        query=sql.SQL("""
            SELECT * FROM {sql_table_name} ORDER BY {sql_column_name}
        """).format(
            sql_table_name = sql.Identifier(table_name),
            sql_column_name = sql.Identifier(column_name)
            )
    cursor.execute(query)
    result_rows = cursor.fetchall()

    return result_rows


@connection_handler
def append_row_in_table(cursor: RealDictCursor, some_dict: dict, table_name):
    table_fields = column_names_dict[table_name]
    intersection_fields = [field for field in table_fields if field in some_dict]    
    value_list = [some_dict[field] for field in intersection_fields ]

    joined_value_list = tuple(n for n in value_list) 
    joined_sql_column_names = sql.SQL(', ').join( sql.Identifier(n) for n in intersection_fields )

    query= sql.SQL('''INSERT INTO {sql_table_name} ({column_names})
            VALUES %(list_of_values)s''').format(
                column_names=joined_sql_column_names, 
                sql_table_name=sql.Identifier(table_name)
            )
    cursor.execute(query,{"list_of_values": joined_value_list})


@connection_handler
def update_data_in_table(cursor: RealDictCursor, some_dict: dict, table_name, id_val=None):
    table_fields = column_names_dict[table_name]
    intersection_fields = [field for field in table_fields if field in some_dict]
    value_list = [some_dict[field] for field in intersection_fields ]
    
    joined_value_list = tuple(n for n in value_list)
    joined_sql_column_names = sql.SQL(', ').join( sql.Identifier(n) for n in intersection_fields )

    if id_val == None: 
        id_value = some_dict['id']
    else:
        id_value = id_val

    query= sql.SQL('''update {sql_table_name}
    set ({column_names})= %(list_of_values)s
    where {id} = %(id_value)s
    ''').format(
        column_names= joined_sql_column_names, 
        id = sql.Identifier('id'),
        sql_table_name=sql.Identifier(table_name)
        )

    cursor.execute(query,{'list_of_values':joined_value_list,'id_value':id_value})


@connection_handler
def delete_data(cursor: RealDictCursor,id_val,table_name):
    query= sql.SQL('''delete from {sql_table_name}
    where {id} = %(id_value)s
    ''').format(id = sql.Identifier('id'),
                sql_table_name= sql.Identifier(table_name))
    cursor.execute(query,{'id_value':id_val})


@connection_handler
def search_pattern_in_triplet_union(
    cursor: RealDictCursor, 
    table_list, 
    search_column_list, 
    union_column_list, 
    pattern_str: str
):
    if len(table_list) != 3 or \
        len(search_column_list) != len(table_list) or len(union_column_list) != len(search_column_list):
        return [{}]
    query=sql.SQL("""
        SELECT regexp_matches({s_column1}, %(pattern_val)s, 'i'), {u_column1} FROM {table1}
        UNION
        SELECT regexp_matches({s_column2}, %(pattern_val)s, 'i'), {u_column2} FROM {table2}
        UNION
        SELECT regexp_matches({s_column3}, %(pattern_val)s, 'i'), {u_column3} FROM {table3}
    """).format(
        s_column1=sql.Identifier(search_column_list[0]),
        s_column2=sql.Identifier(search_column_list[1]),
        s_column3=sql.Identifier(search_column_list[2]),
        u_column1=sql.Identifier(union_column_list[0]),
        u_column2=sql.Identifier(union_column_list[1]),
        u_column3=sql.Identifier(union_column_list[2]),
        table1=sql.Identifier(table_list[0]),
        table2=sql.Identifier(table_list[1]),
        table3=sql.Identifier(table_list[2]),
    )
    cursor.execute(query, {"pattern_val": pattern_str})
    result_rows = cursor.fetchall()

    return result_rows


@connection_handler
def search_pattern_in_triplet_intersect(
    cursor: RealDictCursor, 
    table_list, 
    search_column_list, 
    union_column_list, 
    pattern_str: str
):
    if len(table_list) != 3 or \
        len(search_column_list) != len(table_list) or len(union_column_list) != len(search_column_list):
        return [{}]
    query=sql.SQL("""
        SELECT regexp_matches({s_column1}, %(pattern_val)s, 'i'), {u_column1} FROM {table1}
        INTERSECT
        SELECT regexp_matches({s_column2}, %(pattern_val)s, 'i'), {u_column2} FROM {table2}
        INTERSECT
        SELECT regexp_matches({s_column3}, %(pattern_val)s, 'i'), {u_column3} FROM {table3};
    """).format(
        s_column1=sql.Identifier(search_column_list[0]),
        s_column2=sql.Identifier(search_column_list[1]),
        s_column3=sql.Identifier(search_column_list[2]),
        u_column1=sql.Identifier(union_column_list[0]),
        u_column2=sql.Identifier(union_column_list[1]),
        u_column3=sql.Identifier(union_column_list[2]),
        table1=sql.Identifier(table_list[0]),
        table2=sql.Identifier(table_list[1]),
        table3=sql.Identifier(table_list[2]),
    )
    cursor.execute(query, {"pattern_val": pattern_str})
    result_rows = cursor.fetchall()

    return result_rows


@connection_handler
def delete_tag_by_question_id(cursor: RealDictCursor,id_val,table_name,tag_id_value):
    query= sql.SQL('''delete from {sql_table_name}
    where {question_id} = %(id_value)s
    AND {tag_id} = %(tag_id_value)s
    ''').format(question_id = sql.Identifier('question_id'),
                sql_table_name = sql.Identifier(table_name),
                tag_id= sql.Identifier('tag_id'))
    cursor.execute(query,{'id_value':id_val,'tag_id_value':tag_id_value})


if __name__ == "__main__":
    # print( get_data_from_table('question') )
    # append_row_in_table({'submission_time':datetime.datetime.now(),'view_number':3,'vote_number':7},'comment')
    # update_data_question({'id':3,'title':'New line'})
    pass