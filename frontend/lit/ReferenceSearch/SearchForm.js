import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import IntegerInput from "shared/components/IntegerInput";
import TextInput from "shared/components/TextInput";
import FormActions from "shared/components/FormActions";
import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class SearchForm extends Component {
    render() {
        const {changeSearchTerm, searchForm, submitSearch, resetForm, tagtree} = this.props.store;
        return (
            <form>
                <div className="row">
                    <div className="form-group col-lg-3">
                        <IntegerInput
                            minimum={1}
                            name="id_hawc"
                            label="HAWC ID"
                            helpText="HAWC reference ID."
                            value={searchForm.id}
                            onChange={e => changeSearchTerm("id", parseInt(e.target.value) || "")}
                        />
                    </div>
                    <div className="form-group col-lg-3">
                        <TextInput
                            name="id_db"
                            label="External identifier"
                            helpText="Pubmed ID, DOI, HERO ID, etc."
                            value={searchForm.db_id}
                            onChange={e => changeSearchTerm("db_id", e.target.value)}
                        />
                    </div>
                    <div className="form-group col-lg-3">
                        <IntegerInput
                            minimum={1}
                            name="year"
                            label="Year"
                            helpText="Year of publication"
                            value={searchForm.year}
                            onChange={e => changeSearchTerm("year", parseInt(e.target.value) || "")}
                        />
                    </div>
                    <div className="form-group col-lg-3">
                        <TextInput
                            name="id_journal"
                            label="Journal"
                            value={searchForm.journal}
                            onChange={e => changeSearchTerm("journal", e.target.value)}
                        />
                    </div>
                </div>
                <div className="row">
                    <div className="form-group col-xl-5">
                        <TextInput
                            name="title"
                            label="Title"
                            value={searchForm.title}
                            onChange={e => changeSearchTerm("title", e.target.value)}
                        />
                        <TextInput
                            name="authors"
                            label="Authors"
                            value={searchForm.authors}
                            onChange={e => changeSearchTerm("authors", e.target.value)}
                        />
                        <TextInput
                            name="id_abstract"
                            label="Abstract"
                            value={searchForm.abstract}
                            onChange={e => changeSearchTerm("abstract", e.target.value)}
                        />
                    </div>
                    <div className="form-group col-xl-7">
                        <SelectInput
                            choices={tagtree.choices()}
                            value={searchForm.tags}
                            handleSelect={values => {
                                const ints = values.map(d => parseInt(d));
                                changeSearchTerm("tags", ints);
                            }}
                            label="Tags"
                            helpText="Select one or more tags. If a parent tag is selected, tag children are also considered a match. If multiple tags are selected, references must include all selected tags (or their children)."
                            multiple={true}
                            selectSize={10}
                        />
                    </div>
                </div>
                <FormActions
                    handleSubmit={submitSearch}
                    submitIcon="fa-search"
                    submitText="Search"
                    cancel={resetForm}
                />
            </form>
        );
    }
}

SearchForm.propTypes = {
    store: PropTypes.object,
};

export default SearchForm;
