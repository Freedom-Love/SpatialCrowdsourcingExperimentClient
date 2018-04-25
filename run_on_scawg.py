import scawg_util
import index_server_client
import encoder
from os import makedirs, path
import config
from measure import *

__author__ = 'Jian Xun'


def run_exp(variable_name, distribution, instance_num=None, worker_num_per_instance=None, task_num_per_instance=None,
            task_duration=(1, 2), task_requirement=(1, 3), task_confidence=(0.75, 0.8), worker_capacity=(1, 3),
            worker_reliability=(0.75, 0.8), working_side_length=(0.05, 0.1), batch_interval_time=120, worker_location_mean = 0.5,
                worker_location_variance = 0.2, worker_cluster_number = 3):
    """
    run experiment and return the result
    :type distribution: str
    :type instance_num: int
    :type worker_num_per_instance: int
    :type task_num_per_instance: int
    :type task_duration: tuple
    :type task_requirement: tuple
    :type task_confidence: tuple
    :type worker_capacity: tuple
    :type worker_reliability: tuple
    :type working_side_length: tuple
    :type batch_interval_time: double
    :return:
    """

    # DBUtil.initialize_db()
    DBUtil.clear()
    logger.info('db initialized')


    # statistics including number of assigned(finished) tasks, average moving distance, average workload, running time
    result = {}
    for method in config.output_order:
        result[method] = Measure()

    if distribution == 'real':
        total_real_data_time_length = 3600
        instance_num = total_real_data_time_length/batch_interval_time

    tasks, workers = scawg_util.read_task_and_worker(variable_name, [
        distribution,
        'general',
        'instance=' + str(instance_num),
        'worker_num_per_instance=' + str(worker_num_per_instance),
        'task_num_per_instance=' + str(task_num_per_instance),
        'min_task_duration=' + str(task_duration[0]),
        'max_task_duration=' + str(task_duration[1]),
        'min_task_requirement=' + str(task_requirement[0]),
        'max_task_requirement=' + str(task_requirement[1]),
        'min_task_confidence=' + str(task_confidence[0]),
        'max_task_confidence=' + str(task_confidence[1]),
        'min_worker_capacity=' + str(worker_capacity[0]),
        'max_worker_capacity=' + str(worker_capacity[1]),
        'min_worker_reliability=' + str(worker_reliability[0]),
        'max_worker_reliability=' + str(worker_reliability[1]),
        'min_working_side_length=' + str(working_side_length[0]),
        'max_working_side_length=' + str(working_side_length[1]),
        'batch_interval_time=' + str(batch_interval_time),
        'worker_location_mean=' + str(worker_location_mean),
        'worker_location_variance=' + str(worker_location_variance),
        'worker_cluster_number=' + str(worker_cluster_number)
    ])
    logger.info('data loaded')

    logger.info('set attributes')
    for i in xrange(instance_num):
        worker_ins = workers[i]
        task_ins = tasks[i]
        set_worker_attributes_batch(worker_ins, i, False)
        set_task_attributes_batch(task_ins, i, False)

    session.commit()

    # test on each method in result
    for method in result:
        logger.info('assign ' + method)
        if method == 'workerselectprogressive' and distribution == 'real' and task_duration[0] >= 4:
            continue
        assign = encoder.encode(index_server_client.assign_batch(method))
        # print isinstance(assign, list), isinstance(assign, dict), isinstance(assign, str)
        logger.info('add result of ' + method)
        result[method].add_result(assign, tasks, workers)
        logger.info('finished adding result')

    DBUtil.clear()
    return result


def run_on_variable(distribution, variable_name, values):
    measures = []
    results = {}
    for value in values:
        kwargs = config.get_default()
        kwargs[variable_name] = value
        temp = run_exp(variable_name, distribution, **kwargs)
        for method in temp:
            if method not in results:
                results[method] = {}
            results[method][str(value)] = temp[method].report()
            if len(measures) == 0:
                measures = [x for x in results[method][str(value)]]

    if not path.exists('results'):
        makedirs('results')

    output_file = open('results/' + config.assignment_mode + '_' + distribution + '_' + variable_name + '.csv', 'w')
    for measure in measures:
        output_file.write(measure + '\n')
        output_file.write('method')
        for value in values:
            output_file.write('\t' + str(value))
        output_file.write('\n')
        for method in config.output_order:
            if method not in results:
                continue
            output_file.write(method)
            for value in values:
                output_file.write('\t' + str(results[method][str(value)][measure]))
            output_file.write('\n')
    output_file.close()


def test():
    config.change_to('batched')
    run_on_variable('real', 'task_duration', config.task_duration)
    config.change_to('online')
    run_on_variable('real', 'task_duration', config.task_duration)



def run_experiments_plan(mode):
    if mode == 'online':
        logger.info('online mode')
        config.change_to('online')
    elif mode == 'batched':
        logger.info('batched mode')
        config.change_to('batched')

    for dist in config.distribution:
        if dist != 'real':
            # run_on_variable(dist, 'worker_num_per_instance', config.worker_num_per_instance)
            # run_on_variable(dist, 'task_num_per_instance', config.task_num_per_instance)
            run_on_variable(dist, 'worker_location_mean', config.worker_location_mean)
            run_on_variable(dist, 'worker_location_variance', config.worker_location_variance)
            run_on_variable(dist, 'worker_cluster_number', config.worker_cluster_number)

        run_on_variable(dist, 'task_duration', config.task_duration)
        run_on_variable(dist, 'task_requirement', config.task_requirement)
        run_on_variable(dist, 'task_confidence', config.task_confidence)
        run_on_variable(dist, 'worker_capacity', config.worker_capacity)
        run_on_variable(dist, 'worker_reliability', config.worker_reliability)
        run_on_variable(dist, 'working_side_length', config.working_side_length)
        run_on_variable(dist, 'batch_interval_time', config.batch_interval_time)


if __name__ == '__main__':
    # run_experiments_plan('worker_select')
    # run_experiments_plan('batched')
    test()