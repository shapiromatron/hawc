import React, { Component } from 'react';
import PropTypes from 'prop-types';

import StudyTypeSelector from 'mgmt/TaskTable/components/StudyTypeSelector';
import StudySortSelector from 'mgmt/TaskTable/components/StudySortSelector';

class StudyFilter extends Component {
    constructor(props) {
        super(props);
        let fieldOptions = ['short_citation', 'created'],
            orderOptions = ['ascending', 'descending'];
        this.state = {
            studyTypes: [],
            studySorting: {
                field: fieldOptions[0],
                order: orderOptions[0],
            },
            fieldOptions,
            orderOptions,
        };
        this.clearFilters = this.clearFilters.bind(this);
        this.filterResults = this.filterResults.bind(this);
        this.selectStudyType = this.selectStudyType.bind(this);
        this.selectSort = this.selectSort.bind(this);
    }

    clearFilters() {
        const defaults = {
            studyTypes: [],
            studySorting: {
                field: this.state.fieldOptions[0],
                order: this.state.orderOptions[0],
            },
        };
        this.setState({ ...defaults });
        this.props.selectFilter({
            filterOpts: defaults.studyTypes,
            sortOpts: defaults.studySorting,
        });
    }

    filterResults() {
        this.props.selectFilter({
            filterOpts: this.state.studyTypes,
            sortOpts: this.state.studySorting,
        });
    }

    selectStudyType(types) {
        this.setState({
            studyTypes: types,
        });
    }

    selectSort(opts) {
        this.setState({
            studySorting: opts,
        });
    }

    render() {
        return (
            <div className="container-fluid filterContainer">
                <div className="flexRow-container">
                    <StudyTypeSelector
                        className="flex-1"
                        handleChange={this.selectStudyType}
                    />
                    <StudySortSelector
                        className="flex-1"
                        handleChange={this.selectSort}
                        fieldOptions={this.state.fieldOptions}
                        orderOptions={this.state.orderOptions}
                        studySorting={this.state.studySorting}
                    />
                </div>
                <button
                    className="btn btn-primary"
                    onClick={this.filterResults}
                >
                    Filter & sort studies
                </button>
                <span>&nbsp;</span>
                <button
                    className="btn btn-secondary"
                    onClick={this.clearFilters}
                >
                    Reset
                </button>
            </div>
        );
    }
}

StudyFilter.propTypes = {
    selectFilter: PropTypes.func.isRequired,
};

export default StudyFilter;
