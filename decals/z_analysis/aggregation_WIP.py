#
# import json
#
#
# def get_task_name_from_id(task_id):
#     """
#     Translate the task id (e.g. 'T0') into abbreviated text (e.g. 'features')
#
#     Args:
#         task_id (str): task id of Galaxy Zoo question e.g. 'T0'
#
#     Returns:
#         (str) abbreviated text name of Galaxy Zoo question e.g. 'features'
#
#     """
#     mapping = {
#         'T0': 'features',
#         'T1': 'edge',
#         'T2': 'has_bar',
#         'T3': 'has_spiral',
#         'T4': 'prominent_bulge',
#         'T5': 'merging',
#         'T6': 'odd',
#         'T7': 'rounded',
#         'T8': 'has_bulge',
#         'T9': 'tight_arms',
#         'T10': 'count_arms'
#     }
#     return task_id[mapping]
#
#
# def create_response(classification):
#     annotations = json.loads(classification['annotations'])
#     clean_annotations = get_clean_annotations(annotations)
#     return {
#         'annotations': clean_annotations,
#         'user_id': classification['user_id']
#     }
#
#
# def aggregate_responses(responses):
#     """
#
#     Args:
#         responses (list): in form { user_id: 'user_a', annotations: [{task: 'T0', value: 'smooth'}] }
#
#     Returns:
#         dict of form {T0: {responses: {'smooth': ['user_a', 'user_b']}
#
#     """
#
#     aggregated_responses = {}
#     tasks = set([response['task'] for response in responses])
#     for task in tasks:
#
#         # get all the responses to that task
#         task_responses = []
#         for response in responses:
#             for annotation in response['annotations']:
#                 if annotation['task'] == task:
#                     task_responses.append({
#                         'user_id': response['user_id'],
#                         'response': annotation['value']
#                     })
#
#         # get all the possible answers to that task
#         answer_types = set([task_response['response'] for task_response in task_responses])
#
#         # list users who gave each answer
#
#         # aggregated_responses[task] = {'responses': }