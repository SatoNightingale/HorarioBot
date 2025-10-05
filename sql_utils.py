import sqlite3

def get_db_entry(table: str, select_keys: list[str], primary_key, con: sqlite3.Connection, /, prim_key_name: str = 'id', as_string=False):
    """<pre>query_result = cur.execute(f'SELECT {select_keys} FROM {table} WHERE {prim_key_name} = {primary_key}')
    return query_result.fetchone()</pre>"""
    cur = con.cursor()
    key_signs = ', '.join(select_keys)
    primary_key = primary_key if not as_string else f'"{primary_key}"'
    query = f"SELECT {key_signs} FROM {table} WHERE {prim_key_name} = {primary_key}"
    query_result = cur.execute(query)
    fetched_result = query_result.fetchone()
    return fetched_result

def get_db_list(table: str, select_keys: list[str], primary_key, con: sqlite3.Connection, /, prim_key_name: str = 'id', as_string=False):
    """<pre>query_result = cur.execute(f'SELECT {select_keys} FROM {table} WHERE {prim_key_name} = {primary_key}')
    return query_result.fetchall()</pre>"""
    cur = con.cursor()
    key_signs = ', '.join(select_keys)
    primary_key = primary_key if not as_string else f'"{primary_key}"'
    query = f"SELECT {key_signs} FROM {table} WHERE {prim_key_name} = {primary_key}"
    query_result = cur.execute(query)
    fetched_result = query_result.fetchall()
    return fetched_result