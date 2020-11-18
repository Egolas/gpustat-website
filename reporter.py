from os import name, times
import sqlite3
import time
from typing import Union
import mysql.connector
import yaml
import copy

gpu_info = None
with open('./gpu_info.yaml', 'r') as file:
    gpu_info = yaml.load(file, Loader=yaml.FullLoader)

database_config = {
    'user': 'user',
    'password': 'password',
    'host': '0.0.0.0',
    'database': 'gpustat',
    'raise_on_warnings': True,
    'auth_plugin': 'caching_sha2_password'
}

def init_curr_dict():
    hosts = {}
    for hostname in gpu_info['hosts']:
        host = {
            'ip': gpu_info['hosts'][hostname]['ip'],
            'gpus':list(),
            'all_usernames': list()
        }
        for gpu in gpu_info['hosts'][hostname]['gpus']:
            host['gpus'].append({
                **copy.deepcopy(gpu_info['gpu_info'][gpu]),
                'users':dict()
            })
        hosts[hostname] = host
    return hosts

def to_list(ori):
    if type(ori) is list or type(ori) is tuple:
        res = []
        for x in ori:
            res.append(to_list(x))
        return res
    else:
        return str(ori)

def current_record_qurey(timestamp:float, table: Union[str, None] = None):
    return f'select * from `{table}` where timestamp > {timestamp}'

def get_timeslice_record(start_timestamp:float, end_timestamp:float, table: Union[str, None] = None):
    qurey = f'''select username, sum(gpu_num) as use_time, avg(gpu_num) as avg_gpu_num, avg(sum_mem_usage/gpu_num) as avg_mem_usage
        from
        (
            select hostname,
                timestamp,
                username,
                COUNT(DISTINCT (hostname + `gpu.index`)) as gpu_num,
                sum(`memory.usage`)                      as sum_mem_usage
            from {table}
            where timestamp > {start_timestamp} and timestamp < {end_timestamp} and `memory.usage` > 512
            GROUP BY username, timestamp, hostname
        ) as stat
        group by username'''
    return qurey


def get_record(config:dict, host_names:list, mode='curr', table: Union[str, None] = None):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    if mode == 'curr':
        timestamp = time.time() - 60.0
        record_query = current_record_qurey(timestamp=timestamp, table=table)
    elif mode == 'min':
        end_timestamp = time.time()
        start_timestamp = end_timestamp - 60.0 
        record_query = get_timeslice_record(start_timestamp=start_timestamp, end_timestamp=end_timestamp, table=table)
    elif mode == 'day':
        end_timestamp = time.time()
        start_timestamp = end_timestamp - 60.0 * 60.0 * 24.0
        record_query = get_timeslice_record(start_timestamp=start_timestamp, end_timestamp=end_timestamp, table=table)
    elif mode == 'week':
        end_timestamp = time.time()
        start_timestamp = end_timestamp - 60.0 * 60.0 * 24.0 * 7
        record_query = get_timeslice_record(start_timestamp=start_timestamp, end_timestamp=end_timestamp, table=table)
    elif mode == 'all':
        end_timestamp = time.time()
        start_timestamp = 0.0
        record_query = get_timeslice_record(start_timestamp=start_timestamp, end_timestamp=end_timestamp, table=table)
    else:
        return

    cursor.execute(record_query)
    names = cursor.column_names
    result = list(cursor)
    cursor.close()
    cnx.close()
    return [dict(zip(names,value)) for value in to_list(result)]

if __name__ == '__main__':
    record = get_record(database_config, host_names=['lab407-1', 'lab215-2'], mode='day', table='gpustatistics')
    # print(to_list(record))