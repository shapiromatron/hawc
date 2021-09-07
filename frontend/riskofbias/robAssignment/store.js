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
            .map(d => {
                return {id: d.id, label: d.name};
            })
            .sortBy("id")
            .value();
    }

    @computed get defaultAuthorId() {
        return this.config.users[0].id;
    }

    @action.bound
    update(rob, updates, cb) {
        const {csrf} = this.config,
            url = `/rob/api/review/${rob.id}/update_v2/`;

        _.defaults(updates, rob);

        this.error = false;
        h.handleSubmit(
            url,
            "PATCH",
            csrf,
            updates,
            d => {
                _.assign(rob, d);
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
    create(study, authorId, final, cb) {
        const {csrf} = this.config,
            url = `/rob/api/review/create_v2/`,
            payload = {study: study.id, author: authorId, final, active: true};

        this.error = false;
        h.handleSubmit(
            url,
            "POST",
            csrf,
            payload,
            d => {
                if (final) {
                    // sync frontend w/ backend - only one final review can be active
                    study.robs
                        .filter(rob => rob.final)
                        .forEach(rob => {
                            rob.active = false;
                        });
                }
                study.robs.push(d);
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
