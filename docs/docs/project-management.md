# Project management settings

The project-management module in is designed to allow users to track the progress for data extraction and completion in HAWC. There are four tasks for each study:

1. **Study preparation**: content which should be extracted is clarified and saved to the `Study` instance
2. **Data extraction**: data extracted from paper into HAWC. This can be animal bioassay, epidemiological, epidemiological meta-analyses, or in-vitro data.
3. **QA/QC**: data extracted has been QA/QC.
4. **Risk of Bias:** Risk of bias has been completed.

With each tasks, there are four possible statuses:

1. **Not started**
2. **Started**
3. **Completed**
4. **Abandoned**

Tasks can be assigned to users, and due-dates can also be added (optionally). The status can be manually changed for each task by users using the management dashboard.

In addition, "signals" are automatically fired in order to help users keep track of progress, which automatically change the status of tasks for a particular `Study`. The following signals are implemented:

- When a `Study` is created...
    - If the study preparation task is currently "not started", the task is assigned to the user who created the study, and it is marked "started".
- When data is extracted into a `Study` (i.e. animal bioassy `Experiment`, an epidemiology `Study population`, an epidemiology v2 `Design`, an epidemiology meta-analysis `Study Protocol`, or an *in vitro* `Experiment`)...
    - If the study preparation task is currently "started", the task is marked "complete"
    - If the data extraction task is currently "not started", the task is assigned to the user who added the data, and it is marked "started".
- When `Risk of Bias` is modified...
    - If the risk of bias task is currently "not started", the task is assigned to the user who modified the Risk of Bias, and it is marked "started".
- When a final `Risk of Bias` is completed (which may include conflict resolution)...
    - If the risk of bias task is currently "started", the task is marked "complete"

Unfortunately, we cannot track everything with the automated signals. Therefore, the following task-operations do not have any "signals" associated with them, and must always be manually performed by a user:

- Marking the Data extraction task as "complete" OR "abandoned"
- Marking the QA/QC task as "started"
- Marking the QA/QC task as "completed" OR "abandoned"

!!! note

    Users can always manually modify task status as needed; the signals are designed to help keep track of the tasks where possible automatically in case a user may forget to do so.
