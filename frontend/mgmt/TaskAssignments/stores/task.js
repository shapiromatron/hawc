import _ from "lodash";
import {action, computed, observable} from "mobx";
import h from "shared/utils/helpers";

class TaskAssignmentStore {
    @observable isFetching = false;
    @observable isLoaded = false;
    @observable tasks = [];
    @observable filterTasks = true;

    constructor(rootStore, config) {
        this.rootStore = rootStore;
        this.config = config;
    }

    @action.bound toggleFilterTasks() {
        this.filterTasks = !this.filterTasks;
    }
    @action.bound fetchTasks() {
        if (this.isFetching) {
            return;
        }

        this.isFetching = true;
        this.isLoaded = false;

        const url = `${this.config.tasks.url}?assessment_id=${this.config.assessment_id}`;
        return fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.isFetching = false;
                this.isLoaded = true;
                this.tasks = json;
            });
    }
    @action.bound patchTask(newTask) {
        const url = `${this.config.tasks.submit_url}${newTask.id}/`,
            opts = h.fetchPost(this.config.csrf, newTask, "PATCH");
        fetch(url, opts).then(response => {
            if (response.ok) {
                response.json().then(json => {
                    const index = _.findIndex(this.tasks, {id: json.id});
                    this.tasks[index] = json;
                });
            } else {
                response.json().then(json => console.error(json));
            }
        });
    }

    @computed get tasksByAssessment() {
        return _.chain(this.tasks)
            .filter(task => {
                if (this.filterTasks) {
                    return task.status !== 30 && task.status !== 40;
                } else {
                    return true;
                }
            })
            .filter(task => task.owner.id === this.config.user)
            .groupBy(task => task.study.assessment.name)
            .value();
    }
    @computed get hasTasks() {
        return _.keys(this.tasksByAssessment).length !== 0;
    }
    @computed get showAssessment() {
        return this.config.assessment_id === null;
    }
}

export default TaskAssignmentStore;
