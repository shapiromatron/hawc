import _ from "lodash";
import {action, observable} from "mobx";

class DemoStore {
    @observable items = [
        {id: 1, label: "This is item A", included: true},
        {id: 2, label: "This is item B", included: true},
        {id: 3, label: "This is item C", included: true},
        {id: 4, label: "This is item D", included: true},
    ];
    @action.bound handleOrderChange(id, oldIndex, newIndex) {
        const item = this.items.splice(oldIndex, 1)[0],
            insertIndex = newIndex;
        this.items.splice(insertIndex, 0, item);
    }
    @action.bound handleSelectChange(id, checked) {
        const idx = _.findIndex(this.items, d => d.id === id);
        this.items[idx].included = checked;
    }
}

export default DemoStore;
