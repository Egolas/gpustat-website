from flask import Flask
from flask import render_template #渲染
import reporter
import json
from flask import request

database_config = {
    'user': 'user',
    'password': 'password',
    'host': '0.0.0.0',
    'database': 'gpustat',
    'raise_on_warnings': True,
    'auth_plugin': 'caching_sha2_password'
}
host_names = ['host-1', 'host-2', 'host-2']

app = Flask(__name__)

@app.route('/get_data')
def get_data():
    mode = request.args.get('mode', default = 'curr', type = str)
    response = reporter.get_record(database_config, host_names, mode=mode, table='gpustatistics')
    if mode == 'curr':
        gpu_detail_info = reporter.init_curr_dict()
        for record in response:
            userdict =  gpu_detail_info[record['hostname']]['gpus'][int(record['gpu.index'])]['users']
            if record['username'] not in userdict:
                userdict[record['username']] = {'memory_usage':0.0}
            userdict[record['username']]['memory_usage'] += float(record['memory.usage'])
            gpu_detail_info[record['hostname']]['gpus'][int(record['gpu.index'])]['memory']['free'] -= float(record['memory.usage'])
            if record['username'] not in set(gpu_detail_info[record['hostname']]['all_usernames']):
                gpu_detail_info[record['hostname']]['all_usernames'].append(record['username'])
        response = list()
        for hostname in host_names:
            response_record = {'hostname':hostname, 'records':[], 'ip': gpu_detail_info[hostname]['ip']}
            response_record['records'].append(['GPU name', 'free', *gpu_detail_info[hostname]['all_usernames']])
            for gpu in gpu_detail_info[hostname]['gpus']:
                gpu_record = [gpu['name']]
                gpu_record.append(gpu['memory']['free'])
                for username in gpu_detail_info[hostname]['all_usernames']:
                    if username in gpu['users']:
                        gpu_record.append(gpu['users'][username]['memory_usage'])
                    else:
                        gpu_record.append(0)
                response_record['records'].append(gpu_record)
            response.append(response_record)
    rest = json.dumps(response, indent=4)
    return rest

@app.route('/')
@app.route('/index')
def current():
    page = request.args.get('page', default = 'curr', type = str)
    if page == '':
        page = 'curr'
    context = {
        'title':'GPU Statistics',
        'mode': page,
        'all_options': [
            'curr',
            'min',
            'day',
            'week',
            'all'
        ],
        'hostnames':host_names,
    }
    if page == 'curr':
        return render_template('curr.html',context=context)
    else:
         return render_template('index.html',context=context)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=80)
