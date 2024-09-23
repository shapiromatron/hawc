import * as d3 from "d3";
import _ from "lodash";
import {action, computed, observable, toJS} from "mobx";
import HAWCModal from "shared/utils/HAWCModal";
import h from "shared/utils/helpers";

import {NULL_VALUE} from "../../summary/constants";

class PrismaDatastore {
    @observable dataset = null;
    @observable settings = null;
    @observable objects = null;

    constructor(settings, dataset) {
        this.settings = settings;
        this.dataset = dataset;
        this.objects = settings;
        this.setup_objects();
    }

    initialize() {
        // further initialization for full store use
        this.modal = new HAWCModal();
    }

    set_counts() {
        // add reference counts to lists, boxes, and cards
        // get filter type and id from object
        // get reference count from search id
        // get reference count from tag id
        // set count
    }

    set_text() {
        // format the complete text that will go inside each object
        // add count to the end of text if necessary
        // TODO; add bullets for lists
    }

    setup_objects() {
        this.set_counts();
        this.set_text();
    }

    @computed get settingsHash() {
        return h.hashString(JSON.stringify(this.settings));
    }

    @computed get hasDataset() {
        // return this.dataset !== null && this.dataset.length > 0;
        return true;
    }

    @computed get withinRenderableBounds() {
        // TODO: ensure that the prisma diagram being generated is of a reasonable size.
        return true;
    }

    @computed get getFilterHash() {
        return h.hashString(JSON.stringify(toJS(this.filterWidgetState)));
    }
}

export default PrismaDatastore;
