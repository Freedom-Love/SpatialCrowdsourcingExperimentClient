__author__ = 'Jian Xun'

assignment_mode = 'batched'

output_order = ['geotrucrowdgreedy',
                'geotrucrowdhgr',
                'geocrowdgreedy',
                'geocrowdllep',
                'geocrowdnnp',
                'rdbscdivideandconquer',
                'rdbscsampling'
                ]

output_order_mix_selected = [
                'geotrucrowdhgr',
                'geocrowdllep',
                'rdbscsampling',
                'workerselectbb',
                'workerselectdp',
                'workerselectha'
                ]



output_order_online_mode = ['workerselectprogressive',
                          'workerselectdp',
                          'workerselectbb',
                          'workerselectha'
                          ]

output_order_batched_mode = ['geotrucrowdgreedy',
                            'geotrucrowdhgr',
                            'geocrowdgreedy',
                            'geocrowdllep',
                            'geocrowdnnp',
                            'rdbscdivideandconquer',
                            'rdbscsampling'
                            ]

# total_worker_num = 100000
# distribution = ['gaus', 'skew', 'unif']
distribution = ['real']
# distribution = ['unif']


worker_num_per_instance = [150, 200, 250, 300, 350]
task_num_per_instance = [150, 200, 250, 300, 350]
task_duration = [(1, 2), (2, 3), (3, 4), (4, 5)]
task_requirement = [(1, 3), (3, 5), (5, 7), (7, 9)]
task_confidence = [(0.65, 0.7), (0.75, 0.8), (0.8, 0.85), (0.85, 0.9)]
worker_capacity = [(2, 3), (3, 4), (4, 5), (5, 6)]
# worker_capacity = [(4, 5)]

worker_reliability = [(0.65, 0.7), (0.7, 0.75), (0.75, 0.8), (0.8, 0.85), (0.85, 0.9)]
working_side_length = [(0.05, 0.1), (0.1, 0.15), (0.15, 0.2), (0.2, 0.25)]
batch_interval_time = [30, 60, 120, 180]
worker_cluster_number = [1, 3, 5, 7]
worker_location_mean = [0.1, 0.3, 0.5, 0.7, 0.9]
worker_location_variance = [0.01, 0.03, 0.05, 0.07, 0.1]
worker_speed = [0.01, 0.05, 0.1, 0.15, 0.2]

default_setting = {
    'instance_num': 50,
    'worker_num_per_instance': 150,
    'task_num_per_instance': 150,
    'task_duration': (1, 2),
    'task_requirement': (3, 5),
    'task_confidence': (0.75, 0.8),
    'worker_capacity': (2, 3),
    'worker_reliability': (0.75, 0.8),
    'working_side_length': (0.05, 0.1),
    'batch_interval_time': 120,
    'worker_location_mean': 0.5,
    'worker_location_variance': 0.05,
    'worker_cluster_number': 3,
    'worker_speed': 0.15
}


def change_to(category):
    global output_order
    global assignment_mode
    assignment_mode = category

    if category == 'online':
        output_order = output_order_online_mode
    elif category == 'batched':
        output_order = output_order_batched_mode
    elif category == 'mix':
        output_order = output_order_mix_selected


def get_default():
    return default_setting.copy()
