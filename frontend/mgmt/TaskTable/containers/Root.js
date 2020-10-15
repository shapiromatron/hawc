import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";
import moment from "moment";

import Loading from "shared/components/Loading";

import ScrollToErrorBox from "shared/components/ScrollToErrorBox";
import PopoverTextSpan from "shared/components/PopoverTextSpan";

import {TASK_TYPES, TASK_TYPE_DESCRIPTIONS} from "../constants";
import List from "../components/List";
import StudyFilter from "./StudyFilter";

import "./Root.css";

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        const {store} = this.props;
        store.fetchTasks();
        store.fetchStudies();
    }

    render() {
        if (!this.props.store.isReady) {
            return <Loading />;
        }

        const {store} = this.props,
            {displayAsForm} = store.config,
            taskList = store.taskListByStudy,
            noTasks = taskList.length === 0,
            headers = _.zip(_.values(TASK_TYPES), _.values(TASK_TYPE_DESCRIPTIONS));

        return (
            <div>
                <ScrollToErrorBox error={store.error} />
                <StudyFilter selectFilter={opts => store.filterAndSortStudies(opts)} />
                {noTasks ? (
                    <h4>No studies match the given query.</h4>
                ) : (
                    <table className="table table-condensed">
                        <colgroup>
                            <col width="20%" />
                            <col width="20%" />
                            <col width="20%" />
                            <col width="20%" />
                            <col width="20%" />
                        </colgroup>
                        <thead>
                            <tr>
                                <th>
                                    <PopoverTextSpan
                                        text={"Study"}
                                        title={"Study"}
                                        description={"Selected study object"}
                                    />
                                </th>
                                {headers.map((obj, i) => {
                                    return (
                                        <th key={i}>
                                            <PopoverTextSpan
                                                text={obj[0]}
                                                title={obj[0]}
                                                description={obj[1]}
                                            />
                                        </th>
                                    );
                                })}
                            </tr>
                        </thead>
                        <tbody>
                            {taskList.map(task => {
                                const {study} = task;
                                return (
                                    <tr key={study.id}>
                                        <td>
                                            <a href={study.url}>{study.short_citation}</a>
                                            <br />
                                            <b>Date created: </b>
                                            <span>{moment(study.created).format("L")}</span>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}

                {/*
                    <List
                        component={displayForm ? TaskStudyEdit : TaskStudy}
                        items={taskList}
                        autocompleteUrl={store.config.autocomplete.url}
                        ref={c => (this.list = c)}
                    />
                */}

                {displayAsForm && !noTasks ? (
                    <>
                        <button
                            onClick={event => {
                                event.preventDefault();
                                const updatedData = _.chain(this.list.components)
                                    .filter(component => component != null)
                                    .map(component => component.getChangedData())
                                    .filter(data => !_.isEmpty(data))
                                    .flattenDeep()
                                    .value();
                                store.submitTasks(updatedData);
                            }}
                            className="btn btn-primary">
                            Submit changes
                        </button>
                        <button onClick={store.handleCancel} className="btn space">
                            Cancel
                        </button>
                    </>
                ) : null}
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
