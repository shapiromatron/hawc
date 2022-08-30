import {observable} from "mobx";

import Reference from "../Reference";
import TagTree from "../TagTree";

class Store {
    config = null;
    saveIndicatorElement = null;
    @observable tagtree = null;
    @observable references = [];
    @observable selectedReference = null;
    @observable selectedReferenceTags = null;
    @observable errorOnSave = false;

    constructor(config) {
        this.config = config;
        this.tagtree = new TagTree(config.tags[0]);
        this.references = Reference.sortedArray(config.refs, this.tagtree);
    }
}

export default Store;
