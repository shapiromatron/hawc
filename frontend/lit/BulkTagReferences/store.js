import $ from "$";
import _ from "lodash";
import {action, computed, toJS, observable} from "mobx";

import h from "shared/utils/helpers";

import {deleteArrayElement} from "shared/components/EditableRowData";

class Store {
    config = null;
    @observable dataset = null;

    @observable references = null;
    @observable tags = null;

    @observable datasetIdColumn = null;
    @observable referenceIdColumn = null;
    @observable datasetTagColumn = null;

    @observable datasetTags = [{}];

    constructor(config) {
        this.config = config;
    }

    @action.bound handleFileInput(e) {
        fetch("/lit/api/assessment/100500085/excel-to-json/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Disposition": "attachment; filename=upload",
                "X-CSRFToken": this.config.csrf,
            },
            body: e.target.files[0],
        })
            .then(response => response.json())
            .then(this.hydrateDataset);
        return;
    }

    @action.bound hydrateDataset(json) {
        this.dataset = JSON.parse(json);
    }

    @action.bound getReferences() {
        fetch("/lit/api/assessment/100500085/reference-ids/", h.fetchGet)
            .then(response => response.json())
            .then(json => (this.references = json));
    }

    @action.bound getTags() {
        fetch("/lit/api/assessment/100500085/tags/", h.fetchGet)
            .then(response => response.json())
            .then(json => (this.tags = json));
    }

    @action.bound setDatasetIdColumn(col) {
        // column name in provided dataset for ids
        this.datasetIdColumn = col;
    }

    @action.bound setReferenceIdColumn(col) {
        // column name in returned references for ids
        // either reference_id, hero_id, or pubmed_id
        this.referenceIdColumn = col;
    }

    @action.bound setDatasetTagColumn(col) {
        // column name in provided dataset for tags
        this.datasetTagColumn = col;
    }

    @computed get datasetColumnChoices() {
        return _.chain(this.dataset)
            .first()
            .keys()
            .map(v => [v, v])
            .value();
    }

    get referenceColumnChoices() {
        return [
            ["reference_id", "HAWC ID"],
            ["hero_id", "HERO ID"],
            ["pubmed_id", "PUBMED ID"],
        ];
    }

    @computed get datasetTagChoices() {
        let tags = _.chain(this.dataset)
            .map(v => v[this.datasetTagColumn])
            .filter(v => v)
            .value();
        return _.map(tags, v => [v, v]);
    }

    @computed get HAWCTagChoices() {
        return _.map(this.tags, v => [v["id"], v["nested_name"]]);
    }

    @action.bound createDatasetTag() {
        this.datasetTags.push({});
    }

    @action.bound deleteDatasetTag(index) {
        deleteArrayElement(this.datasetTags, index);
    }

    @action.bound setDatasetTagString(index, value) {
        this.datasetTags[index].string = value;
    }

    @action.bound setDatasetTagId(index, value) {
        this.datasetTags[index].id = value;
    }

    @computed get referenceMap() {
        let ids = _.map(this.dataset, v => v[this.datasetIdColumn]),
            matchingReferences = _.chain(this.references)
                .filter(v => _.includes(ids, v[this.referenceIdColumn]))
                .map(v => ({[v[this.referenceIdColumn]]: v["reference_id"]}))
                .value();
        return _.assign({}, ...matchingReferences);
    }

    @computed get tagMap() {
        let tags = _.map(this.datasetTags, v => ({[v.string]: v.id}));
        return _.assign({}, ...tags);
    }

    @computed get datasetMap() {
        let ids = _.map(_.keys(this.referenceMap), v => parseInt(v)),
            tags = _.keys(this.tagMap),
            foobar = _.chain(this.dataset)
                .filter(v => _.includes(ids, v[this.datasetIdColumn]))
                .filter(v => _.includes(tags, String(v[this.datasetTagColumn])))
                .map(v => ({
                    reference_id: this.referenceMap[v[this.datasetIdColumn]],
                    tag_id: this.tagMap[v[this.datasetTagColumn]],
                }))
                .value();
        return foobar;
    }
}

export default Store;
