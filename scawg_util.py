import subprocess
from os import listdir, makedirs, path
from shutil import rmtree, move
from math import log

__author__ = 'Jian Xun'


__initial__ = False


class Worker:
    def __init__(self):
        self.id = None
        self.longitude = None
        self.latitude = None
        self.capacity = 1
        self.activeness = 1
        self.velocity = 0.25
        self.min_lat = None
        self.min_lon = None
        self.max_lat = None
        self.max_lon = None
        self.reliability = 1
        self.velocity = None
        self.min_direction = None
        self.max_direction = None

    def from_general(self, params):
        """
        Args:
            params(list): a list of params parsed from SCAWG output file
        """
        self.id = params[0]
        self.latitude = params[1]
        self.longitude = params[2]
        self.capacity = params[3]
        self.activeness = params[4]
        # only use one parameter to generate a square region
        self.min_lat = params[5][0]
        self.min_lon = params[5][1]
        self.max_lat = params[5][2]
        self.max_lon = params[5][3]
        self.reliability = params[6]
        self.velocity = params[7]


class Task:
    def __init__(self):
        self.id = None
        self.longitude = None
        self.latitude = None
        self.arrival_time = None
        self.expire_time = None
        self.require_answer_count = 1
        self.assigned = 0
        self.entropy = 0.5
        self.confidence = 0.5

    def from_general(self, params):
        self.latitude = params[0]
        self.longitude = params[1]
        self.arrival_time = params[2]
        self.expire_time = params[3]
        self.require_answer_count = params[4]
        self.confidence = params[5]
        self.entropy = params[6]


def run_jar(params):
    print 'run params', str(params)
    subprocess.call(['java', '-jar', './SCDataGenerator.jar'] + params)


def parse_line(line):
    """
    parse the line to several parts, a part can be either a string or a list.
    Args:
        line(str):

    Returns: a list of strings or lists or both

    """
    result = []
    cur = 0
    while cur < len(line):
        if line[cur] == '[':
            last = line.index(']', cur)
            result.append(parse_line(line[cur + 1: last]))
            cur = last + 2
        else:
            try:
                last = line.index(';', cur)
                result.append(line[cur: last])
                cur = last + 1
            except ValueError:
                result.append(line[cur:])
                cur = len(line)
    for i in xrange(len(result)):
        if isinstance(result[i], str) and '.' in result[i]:
            result[i] = float(result[i])
        if isinstance(result[i], str) and '.' not in result[i]:
            result[i] = int(result[i])
    return result


def generate_instance(options):
    run_jar(options)


def generate_general_task_and_worker(variable_name, dist, options):
    run_jar(['general'] + options)
    source_dirct = 'res/output/'
    dirct = dist
    prefix_task = dist+'_tasks'
    prefix_worker = dist+'_workers'


    for option in options:
        if option.startswith('instance='):
            instance = int(option[9:])
    if 'real' in options:
        source_dirct = 'dataset/real'
        dirct = 'real'
        prefix_task = 'tasks'
        prefix_worker = 'workers'

    # save data to the specific directory
    sub_dir = param_to_dir_name(variable_name, options)
    parent_dir = path.join('dataset', dirct, 'task')
    if not path.exists(path.join(parent_dir, sub_dir)):
        makedirs(path.join(parent_dir, sub_dir))
    for i in xrange(instance):
        file_name = prefix_task + str(i) + '.txt'
        move(path.join(source_dirct, 'task/tasks' + str(i) + '.txt'), path.join(parent_dir, sub_dir, file_name))

    parent_dir = path.join('dataset', dirct, 'worker')
    if not path.exists(path.join(parent_dir, sub_dir)):
        makedirs(path.join(parent_dir, sub_dir))
    for i in xrange(instance):
        file_name = prefix_worker + str(i) + '.txt'
        move(path.join(source_dirct, 'worker/workers' + str(i)+'.txt'), path.join(parent_dir, sub_dir, file_name))




def read_task_and_worker(variable_name, dist, options):
    dirct = dist
    prefix_task = dist + '_tasks'
    prefix_worker = dist + '_workers'

    for option in options:
        if option.startswith('instance='):
            instance = int(option[9:])
    if 'real' in options:
        dirct = 'real'
        prefix_task = 'tasks'
        prefix_worker = 'workers'

    sub_dir = param_to_dir_name(variable_name, options)
    tasks = []
    for i in xrange(instance):
        temp = []
        f = open(path.join('dataset', dirct, 'task', sub_dir, prefix_task + str(i) + '.txt'), 'r')
        for line in f:
            task = Task()
            task.from_general(parse_line(line))
            temp.append(task)
        f.close()
        tasks.append(temp)
    workers = []
    for i in xrange(instance):
        temp = []
        f = open(path.join('dataset', dirct, 'worker', sub_dir, prefix_worker + str(i) + '.txt'), 'r')
        for line in f:
            worker = Worker()
            worker.from_general(parse_line(line))
            temp.append(worker)
        f.close()
        workers.append(temp)
    compute_entropy(tasks, workers)
    return tasks, workers


def compute_entropy(tasks, workers):
    for t_ins in xrange(len(tasks)):
        for task in tasks[t_ins]:
            # calculate entropy for this task
            total_num = 0.0
            distinct = {}
            for w_ins in xrange(t_ins + 1):
                for worker in workers[w_ins]:
                    dis_lon = worker.longitude - task.longitude if worker.longitude > task.longitude\
                        else task.longitude - worker.longitude
                    dis_lat = worker.latitude - task.latitude if worker.latitude > task.latitude\
                        else task.latitude - worker.latitude
                    if dis_lon <= 0.1 and dis_lat < 0.1:
                        w_id = str(worker.id)
                        if w_id in distinct:
                            distinct[w_id] += 1
                        else:
                            distinct[w_id] = 1
                        total_num += 1
            entropy = 0.0
            for w_id in distinct:
                pl = distinct[w_id] / total_num
                entropy -= pl * log(pl)
            task.entropy = entropy
            # print 'entropy is', entropy


def param_to_dir_name(variable_name, options):
    for option in options:
        if variable_name in option:
            return variable_name + '/' + option.split('=')[1].replace(' ', '')
    raise Exception('cannot find variable ' + variable_name + ' in options ' + str(options))


def clear_dir():
    files = listdir('./dataset')
    if 'uni' in files:
        rmtree('./dataset/uni')
    if 'real' in files:
        _files = listdir('./dataset/real')
        if 'task' in _files:
            rmtree('./dataset/real/task')
        if 'worker' in _files:
            rmtree('./dataset/real/worker')
    files = listdir('./res')
    if 'dataset' in files:
        rmtree('./res/dataset')


if __name__ == '__main__':
    line = '598;74.16063640794154;45.10879073935417;19;0.7866654507704679;[74.16063640794154;45.10879073935417;' \
           '0.0;0.0]0.3106544569620695'
    print parse_line(line)
    worker = Worker()
    worker.from_general(parse_line(line))
    print worker.min_lon, worker.min_lat, worker.max_lon, worker.max_lat
