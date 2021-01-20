import RobStore from "./rob";
import TaskStore from "./task";

class RootStore {
    constructor(config) {
        this.rob = new RobStore(this, config);
        this.task = new TaskStore(this, config);
    }
}

export default RootStore;
