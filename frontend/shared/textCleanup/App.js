import "./App.css";

import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Loading from "shared/components/Loading";
import h from "shared/utils/helpers";

import Breadcrumbs from "./Breadcrumbs";
import GroupedObjectList from "./GroupedObjectList";

@inject("store")
@observer
class App extends Component {
    constructor(props) {
        super(props);
        this.renderCleanupField = this.renderCleanupField.bind(this);
        this.renderSelectField = this.renderSelectField.bind(this);
        this.renderAssessmentMetadata = this.renderAssessmentMetadata.bind(this);
    }
    componentDidMount() {
        this.props.store.loadAssessmentMetadata();
    }
    render() {
        const {store} = this.props;

        if (store.isLoading) {
            return <Loading />;
        }

        let func;
        if (store.selectedField) {
            func = this.renderCleanupField;
        } else if (store.selectedModel) {
            func = this.renderSelectField;
        } else {
            func = this.renderAssessmentMetadata;
        }
        return (
            <div>
                <Breadcrumbs />
                {func()}
            </div>
        );
    }
    renderCleanupField() {
        const {store} = this.props;
        return (
            <div>
                <h3>
                    Cleanup {h.titleCase(store.selectedModel.title)} →{" "}
                    {h.titleCase(store.selectedField)}
                </h3>
                {store.isLoadingObjects ? <Loading /> : null}
                {store.objects ? <GroupedObjectList /> : null}
            </div>
        );
    }
    renderSelectField() {
        const {store} = this.props;
        return (
            <div>
                <h3>Cleanup {h.titleCase(store.selectedModel.title)}</h3>
                {store.modelCleanupFields ? (
                    <ul className="list-group">
                        {store.modelCleanupFields.map(field => (
                            <li className="list-group-item" key={field}>
                                <a href="#" onClick={() => store.selectField(field)}>
                                    {field}
                                </a>
                            </li>
                        ))}
                    </ul>
                ) : null}
            </div>
        );
    }
    renderAssessmentMetadata() {
        const {store} = this.props;
        const groupedItems = _.groupBy(store.assessmentMetadata.items, "app");
        return (
            <div>
                <h2>Cleanup {store.assessmentMetadata.name}</h2>
                <p className="form-text text-muted">
                    After data has been initially extracted, this module can be used to update and
                    standardize text which was used during data extraction.
                </p>
                <b>To begin, select a data-type to cleanup</b>
                <ul>
                    {Object.entries(groupedItems)
                        .filter(([_app, items]) => items.some(item => item.count > 0))
                        .map(([app, items]) => {
                            return (
                                <div key={app}>
                                    <h4 className="mt-3">{app}:</h4>
                                    <ul className="list-group">
                                        {items
                                            .filter(item => item.count > 0)
                                            .map(d => {
                                                return (
                                                    <a
                                                        className="list-group-item list-group-item-action"
                                                        key={d.title}
                                                        href="#"
                                                        onClick={() => store.selectModel(d)}>
                                                        {d.title}
                                                        <span className="badge badge-primary badge-pill ml-2">
                                                            {d.count}
                                                        </span>
                                                    </a>
                                                );
                                            })}
                                    </ul>
                                </div>
                            );
                        })}
                </ul>
            </div>
        );
    }
}
App.propTypes = {
    store: PropTypes.object,
};

export default App;
