import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

// import Select
import RadioInput from "shared/components/RadioInput";
import SelectInput from "shared/components/SelectInput";
import {STUDY_TYPE_CHOICES} from "../constants";

@inject("store")
@observer
class StudyFilter extends Component {
    render() {
        const {store} = this.props;
        return (
            <div className="container-fluid filterContainer">
                <div className="row">
                    <div className="col-md-4">
                        <SelectInput
                            choices={STUDY_TYPE_CHOICES}
                            value={store.filters.studyTypeFilters}
                            handleSelect={values => store.updateFilters("studyTypeFilters", values)}
                            multiple={true}
                            selectSize={4}
                            label="Study type filter (optional):"
                        />
                    </div>
                    <div className="col-md-4">
                        <RadioInput
                            label="Sort studies by:"
                            name="sortBy"
                            onChange={value => store.updateFilters("sortBy", value)}
                            value={store.filters.sortBy}
                            choices={[
                                {id: "short_citation", label: "Short citation"},
                                {id: "created", label: "Creation date"},
                            ]}
                        />
                    </div>
                    <div className="col-md-4">
                        <RadioInput
                            label="Order studies by:"
                            name="orderBy"
                            onChange={value => store.updateFilters("orderBy", value)}
                            value={store.filters.orderBy}
                            choices={[
                                {id: "asc", label: "Ascending"},
                                {id: "desc", label: "Descending"},
                            ]}
                        />
                    </div>
                </div>
            </div>
        );
    }
}

StudyFilter.propTypes = {
    store: PropTypes.object,
};

export default StudyFilter;
