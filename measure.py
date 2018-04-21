import math
from db_util import *
from logger import logger

# maps scawg id to gmission id (the same as index of vworkers)
worker_dic = {}
worker_used = 0

class Measure:
    total_assignment = None
    running_time = None
    worker_dic = None
    task_dic = None
    total_moving_dis = None
    assigned_workers = None
    task_worker = None
    finished = None
    average_workload = None

    def __init__(self):
        self.total_assignment = 0
        self.finished = 0
        self.total_moving_dis = 0
        self.average_workload = 0
        self.running_time = 0
        self.task_dic = {}
        self.worker_dic = {}
        self.assigned_workers = {}
        self.task_worker = {}

    def add_result(self, assigns, tasks, workers):
        for ins in tasks:
            for task in ins:
                tid = str(task.id)
                self.task_dic[tid] = task
                self.task_worker[tid] = []
        for ins in workers:
            for worker in ins:
                wid = get_id(worker.id)
                self.worker_dic[str(wid)] = worker
        for assign in assigns:
            if assign['taskId'] == -1:
                self.running_time += assign['workerId']
            else:
                self.total_assignment += 1
                wid = str(assign['workerId'])
                tid = str(assign['taskId'])
                # print assign['workerId'],  wid
                if wid not in self.assigned_workers:
                    self.assigned_workers[wid] = wid
                if wid in self.task_worker[tid]:
                    logger.error('!!!!!!! duplicate assignment !!!!!!!')
                self.task_worker[tid].append(wid)
                self.task_dic[tid].assigned += 1
                self.total_moving_dis += Measure.moving_dis(self.task_dic[tid], self.worker_dic[wid])

    @staticmethod
    def ars(workers, level, confidence, neg_count, task):
        if level == len(workers) or level - neg_count == task.require_answer_count:
            return confidence
        if level > 10 or confidence < 0.0000001:
            return confidence
        # assume this worker gives a positive answer
        answer = Measure.ars(workers, level + 1, confidence * workers[level].reliability, neg_count, task)
        if answer > task.confidence:
            return 1
        # assume this worker gives a negative answer
        if neg_count < (len(workers) - 1) / 2:
            answer += Measure.ars(workers, level + 1, confidence * (1 - workers[level].reliability), neg_count + 1,
                                  task)
        return answer

    @staticmethod
    def satisfy_conf(task, workers):
        # maximum possible worker num
        if len(workers) >= 17:
            return True
        return Measure.ars(workers, 0, 1, 0, task) >= task.confidence

    @staticmethod
    def moving_dis(task, worker):
        return math.sqrt((task.longitude - worker.longitude) ** 2 + (task.latitude - worker.latitude) ** 2)

    def report(self):
        self.finished = 0
        finished_conf = 0
        for tid in self.task_dic:
            if len(self.task_worker[tid]) >= self.task_dic[tid].require_answer_count:
                self.finished += 1
                if Measure.satisfy_conf(self.task_dic[tid], [self.worker_dic[wid] for wid in self.task_worker[tid]]):
                    finished_conf += 1
        return {
            'average_moving_dis':
                0 if len(self.assigned_workers) == 0 else self.total_moving_dis / len(self.assigned_workers),
            'finished_task_num': self.finished,
            'finished_task_num_conf': finished_conf,
            'running_time': self.running_time / 1000.0
        }
            # 'task_num': len(self.task_dic),
            # 'worker_num': len(self.worker_dic),
            # 'assigned_worker_num': len(self.assigned_workers),
            # 'average_moving_dis':
            #     0 if len(self.assigned_workers) == 0 else self.total_moving_dis / len(self.assigned_workers),
            # 'average_moving_distance_per_WT_pair':
            #     0 if self.total_assignment == 0 else self.total_moving_dis / self.total_assignment,
            # 'average_workload':
            #     0 if len(self.assigned_workers) == 0 else (self.total_assignment + 0.0) / len(self.assigned_workers),
            # 'total_assignment': self.total_assignment,




def get_id(scawg_id):
    global worker_dic
    global worker_used
    if str(scawg_id) in worker_dic:
        return worker_dic[str(scawg_id)]
    else:
        worker_used += 1
        worker_dic[str(scawg_id)] = worker_used
        return worker_used



def set_worker_attributes_batch(workers, time, commit=True):
    for worker in workers:
        real_id = get_id(worker.id)
        DBUtil.set_worker_attributes(uid=real_id, longitude=worker.longitude, latitude=worker.latitude,
                                      capacity=worker.capacity, reliability=worker.reliability,
                                      min_lon=worker.min_lon, min_lat=worker.min_lat, max_lon=worker.max_lon,
                                      max_lat=worker.max_lat, is_online=time, commit=False)
    if commit:
        session.commit()


def set_task_attributes_batch(tasks, time, commit=True):
    for task in tasks:
        hit_id = DBUtil.create_hit(task.longitude, task.latitude, task.arrival_time, task.expire_time,
                                    task.require_answer_count,
                                    task.entropy, task.confidence, is_valid=time, commit=False)
        task.id = hit_id
    if commit:
        session.commit()
