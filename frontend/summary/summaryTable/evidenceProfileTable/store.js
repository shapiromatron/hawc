import _ from "lodash";
import {action, autorun, computed, observable, toJS} from "mobx";

import h from "shared/utils/helpers";

class EvidenceProfileTableStore {
    @observable editMode = false;
    @observable settings = null;
    @observable showCellModal = false;
    @observable stagedContent = null;
    @observable editErrorText = "";
    @observable showColumnEdit = false;

    constructor(editMode, settings, editRootStore) {
        this.editMode = editMode;
        this.settings = settings;
        this.editRootStore = editRootStore;
        if (editMode && editRootStore) {
            autorun(() => {
                this.editRootStore.updateTableContent(JSON.stringify(this.settings), false);
            });
        }
    }

    @computed get numSummaryRows() {
        return (
            6 +
            Math.max(this.settings.exposed_human.cell_rows.length, 1) +
            Math.max(this.settings.animal.cell_rows.length, 1) +
            Math.max(this.settings.mechanistic.cell_rows.length, 1)
        );
    }

    // inject new settings from parent object
    @action.bound updateSettings(settings) {
        this.settings = settings;
    }
}

export default EvidenceProfileTableStore;
