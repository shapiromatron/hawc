export const REQUEST_TASKS = 'REQUEST_TASKS';
export const RECEIVE_TASKS = 'RECEIVE_TASKS';
export const PATCH_TASK = 'PATCH_TASK';
export const SUBMIT_TASKS = 'SUBMIT_TASKS';
export const SUBMIT_FINISHED = 'SUBMIT_FINISHED';
export const REQUEST_STUDIES = 'REQUEST_STUDIES';
export const RECEIVE_STUDIES = 'RECEIVE_STUDIES';
export const FILTER_STUDY_ON_TYPE = 'FILTER_STUDY_ON_TYPE';
export const SORT_STUDIES = 'SORT_STUDIES';
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
    40: 'Risk of bias/study evaluation completed',
};
export const TASK_TYPE_DESCRIPTIONS = {
    10: 'Content which should be extracted from reference is clarified and saved to the Study instance for data-extractors.',
    20: 'Data is extracted from reference into HAWC. This can be animal bioassay, epidemiological, epidemiological meta-analyses, or in-vitro data.',
    30: 'Data extracted has been QA/QC.',
    40: 'Risk of bias/study evaluation has been completed for this reference (if enabled for this assessment).',
};
export const STUDY_TYPES = {
    bioassay: 'Animal bioassay',
    epi: 'Epidemiology',
    epi_meta: 'Epidemiology meta-analysis',
    in_vitro: 'In vitro',
};
