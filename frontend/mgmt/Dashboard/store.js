import {action, observable} from "mobx";
import h from "shared/utils/helpers";

class MgmtDashboardStore {
    @observable isFetching = false;
    @observable tasks = null;
    @observable error = null;

    constructor(config) {
        this.config = config;
    }

    @action.bound fetchTasks() {
        this.isFetching = true;
        let {assessment_id} = this.config;
        const url = `/mgmt/api/task/?assessment_id=${assessment_id}`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.tasks = json;
                this.error = null;
                this.isFetching = false;
            })
            .catch(error => {
                this.tasks = null;
                this.error = error;
                this.isFetching = false;
            });
    }
}
export default MgmtDashboardStore;
