import _ from "lodash";
import {action, computed, observable} from "mobx";
import h from "shared/utils/helpers";

import StudyRobStore from "../stores/StudyRobStore";

class RobAssignmentStore extends StudyRobStore {
    @observable studies = [];
    @observable error = false;

    constructor(config) {
        super();
        this.config = config;
        this.studies = config.studies;
        _.unset(config, "studies");
    }

    @computed get individualReviewsRequired() {
        return this.config.number_of_reviewers > 1;
    }

    @computed get authorOptions() {
        return _.chain(this.config.users)
            .sortBy("last_name", "id")
            .map(d => {
                return {id: d.id, label: `${d.first_name} ${d.last_name}`};
            })
            .value();
    }

    @computed get defaultAuthorId() {
        return this.config.users[0].id;
    }

    @action.bound
    update(study, rob, updates, cb) {
        const {csrf} = this.config,
            url = `/rob/api/review/${rob.id}/assignment/`;

        _.defaults(updates, rob);

        this.error = false;
        h.handleSubmit(
            url,
            "PATCH",
            csrf,
            updates,
            d => {
                _.assign(rob, d);
                this.syncActiveFinal(study, d);
                if (cb) {
                    cb();
                }
            },
            d => {
                this.error = true;
                console.error("Failure", d);
            },
            d => {
                this.error = true;
                console.error("Error", d);
            }
        );
    }

    @action.bound
    syncActiveFinal(study, d) {
        // sync frontend w/ backend - only one final review can be active
        if (d.final && d.active) {
            study.robs
                .filter(rob => rob.final)
                .filter(rob => rob.id !== d.id)
                .forEach(rob => {
                    rob.active = false;
                });
        }
    }

    @action.bound
    create(study, authorId, final, cb) {
        const {csrf} = this.config,
            url = `/rob/api/review/assignment/`,
            payload = {study: study.id, author: authorId, final, active: true};

        this.error = false;
        h.handleSubmit(
            url,
            "POST",
            csrf,
            payload,
            d => {
                study.robs.push(d);
                this.syncActiveFinal(study, d);
                if (cb) {
                    cb();
                }
            },
            d => {
                this.error = true;
                console.error("Failure", d);
            },
            d => {
                this.error = true;
                console.error("Error", d);
            }
        );
    }
}

export default RobAssignmentStore;
