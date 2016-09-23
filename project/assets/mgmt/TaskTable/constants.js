export const REQUEST_TASKS = 'REQUEST_TASKS';
export const RECEIVE_TASKS = 'RECEIVE_TASKS';
export const PATCH_TASK = 'PATCH_TASK';
export const SUBMIT_TASKS = 'SUBMIT_TASKS';
export const SUBMIT_FINISHED = 'SUBMIT_FINISHED';
export const REQUEST_STUDIES = 'REQUEST_STUDIES';
export const RECEIVE_STUDIES = 'RECEIVE_STUDIES';
export const STATUS = {
    10: { color: '#CFCFCF' /* grey */, type: 'not started' },
    20: { color: '#FFCC00' /* yellow */, type: 'started' },
    30: { color: '#00CC00' /* green */, type: 'completed' },
    40: { color: '#CC3333' /* red */, type: 'abandoned' },
};
export const TASK_TYPES = {
    10: 'Data preparation',
    20: 'Data extraction',
    30: 'QA/QC',
    40: 'Risk of bias completed',
};
