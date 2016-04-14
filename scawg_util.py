import subprocess
from os import listdir

__author__ = 'Jian Xun'


__initial__ = False


class Worker:
    id = None
    longitude = None
    latitude = None
    capacity = 1
    activeness = 1
    min_lat = None
    min_lon = None
    max_lat = None
    max_lon = None
    reliability = 1
    velocity = None
    min_direction = None
    max_direction = None

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
        dis = params[5][0]
        self.max_lat = self.latitude + dis / 2
        self.max_lon = self.longitude + dis / 2
        self.min_lat = self.latitude - dis / 2
        self.min_lon = self.longitude - dis / 2
        self.reliability = params[6]


class Task:
    id = None
    longitude = None
    latitude = None
    arrival_time = None
    expire_time = None
    require_answer_count = 1
    assigned = 0
    entropy = 0.5
    confidence = 0.5

    def from_general(self, params):
        self.latitude = params[0]
        self.longitude = params[1]
        self.arrival_time = params[2]
        self.expire_time = params[3]
        self.require_answer_count = params[4]
        self.confidence = params[5]
        self.entropy = params[6]


def run_jar(params):
    subprocess.call(['java', '-jar', './GeocrowdDataGenerator.jar'] + params)


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


def generate_instance(options=[]):
    run_jar(['new_instance'] + options)
    global __initial__
    __initial__ = True


def generate_general_task_and_worker():
    global __initial__
    if not __initial__:
        generate_instance()
    run_jar(['general'])
    files = listdir('./dataset/uni/task')
    tasks = []
    for name in files:
        temp = []
        file = open('./dataset/uni/task/' + name, 'r')
        for line in file:
            task = Task()
            task.from_general(parse_line(line))
            temp.append(task)
        file.close()
        tasks.append(temp)
    files = listdir('./dataset/uni/worker')
    workers = []
    for name in files:
        temp = []
        file = open('./dataset/uni/worker/' + name, 'r')
        for line in file:
            worker = Worker()
            worker.from_general(parse_line(line))
            temp.append(worker)
        file.close()
        workers.append(temp)
    return tasks, workers


if __name__ == '__main__':
    line = '598;74.16063640794154;45.10879073935417;19;0.7866654507704679;[74.16063640794154;45.10879073935417;0.0;0.0]0.3106544569620695'
    print parse_line(line)
    worker = Worker()
    worker.from_general(parse_line(line))
    print worker.min_lon, worker.min_lat, worker.max_lon, worker.max_lat