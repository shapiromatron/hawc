import React from "react";
import {observable, action, computed} from "mobx";
import {modelChoices} from "./constants";
import h from "shared/utils/helpers";

class ChemicalsStore {
    @observable search = "";
    @observable choice = modelChoices[0].id;
    @observable dataset = null;

    @action.bound fetchDataset() {
        const url = `/assessment/api/dashboard/chemicals/?model=${this.choice}`;
        return fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => (this.dataset = json))
            .catch(ex => console.error("Dataset fetch failed", ex));
    }
    @action.bound changeSearch(newSearch) {
        this.search = newSearch;
    }
    @action.bound changeChoice(newChoice) {
        this.choice = newChoice;
        this.fetchDataset();
    }
    @computed get matchingDataset() {
        return this.dataset.filter(row =>
            row["cas"].toLowerCase().includes(this.search.toLowerCase())
        );
    }
    @computed get matchingRenderer() {
        if (this.choice == "assessment") {
            return {
                name: row => {
                    return <a href={`/assessment/${row.id}/`}>{row.name}</a>;
                },
            };
        } else if (this.choice == "experiment") {
            return {
                name: row => {
                    return <a href={`/animal/experiment/${row.id}/`}>{row.name}</a>;
                },
            };
        } else if (this.choice == "ivchemical") {
            return {
                name: row => {
                    return <a href={`/invitro/chemical/${row.id}/`}>{row.name}</a>;
                },
            };
        }
    }
}

const store = new ChemicalsStore();

export default store;
