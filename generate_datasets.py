import scawg_util
import config
from logger import logger


def generate_data_on_variable(distribution, variable_name, values):
    for value in values:
        kwargs = config.get_default()
        kwargs[variable_name] = value
        generate_data(variable_name, distribution, **kwargs)

def generate_data(variable_name, distribution, instance_num=None, worker_num_per_instance=None, task_num_per_instance=None,
                  task_duration=(1, 2), task_requirement=(1, 3), task_confidence=(0.75, 0.8), worker_capacity=(1, 3),
                  worker_reliability=(0.75, 0.8), working_side_length=(0.05, 0.1)):
    """
        generate data according to settings
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
    """
    logger.info('generating data')
    if distribution == 'real':
        instance_num = 30

    scawg_util.generate_general_task_and_worker(variable_name, [
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
        'max_working_side_length=' + str(working_side_length[1])
    ])
    logger.info('data generated')


if __name__ == '__main__':
    for dist in config.distribution:
        if dist != 'real':
            generate_data_on_variable(dist, 'worker_num_per_instance', config.worker_num_per_instance)
            generate_data_on_variable(dist, 'task_num_per_instance', config.task_num_per_instance)
        generate_data_on_variable(dist, 'task_duration', config.task_duration)
        generate_data_on_variable(dist, 'task_requirement', config.task_requirement)
        generate_data_on_variable(dist, 'task_confidence', config.task_confidence)
        generate_data_on_variable(dist, 'worker_capacity', config.worker_capacity)
        generate_data_on_variable(dist, 'worker_reliability', config.worker_reliability)
        generate_data_on_variable(dist, 'working_side_length', config.working_side_length)