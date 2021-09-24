import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import IntegerInput from "shared/components/IntegerInput";
import TextInput from "shared/components/TextInput";
import FormActions from "shared/components/FormActions";

@inject("store")
@observer
class SearchForm extends Component {
    render() {
        const {changeSearchTerm, searchForm, submitSearch, resetForm} = this.props.store;
        return (
            <form>
                <div className="row">
                    <div className="form-group col-md-4">
                        <IntegerInput
                            minimum={1}
                            name="id_hawc"
                            label="HAWC ID"
                            helpText="HAWC reference ID."
                            value={searchForm.id}
                            onChange={e =>
                                changeSearchTerm("id", parseInt(e.target.value) || undefined)
                            }
                        />
                    </div>
                    <div className="form-group col-md-4">
                        <IntegerInput
                            minimum={1}
                            name="id_db"
                            label="Database unique identifier"
                            helpText="Identifiers may include Pubmed ID, HERO ID, etc."
                            value={searchForm.db_id}
                            onChange={e =>
                                changeSearchTerm("db_id", parseInt(e.target.value) || undefined)
                            }
                        />
                    </div>
                    <div className="form-group col-md-4">
                        <IntegerInput
                            minimum={1}
                            name="year"
                            label="Year"
                            helpText="Year of publication"
                            value={searchForm.year}
                            onChange={e =>
                                changeSearchTerm("year", parseInt(e.target.value) || undefined)
                            }
                        />
                    </div>
                </div>
                <div className="row">
                    <div className="form-group col-md-6">
                        <TextInput
                            name="title"
                            label="Title"
                            value={searchForm.title}
                            onChange={e => changeSearchTerm("title", e.target.value)}
                        />
                    </div>
                    <div className="form-group col-md-6">
                        <TextInput
                            name="authors"
                            label="Authors"
                            value={searchForm.authors}
                            onChange={e => changeSearchTerm("authors", e.target.value)}
                        />
                    </div>
                </div>
                <div className="row">
                    <div className="form-group col-md-6">
                        <TextInput
                            name="id_journal"
                            label="Journal"
                            value={searchForm.journal}
                            onChange={e => changeSearchTerm("journal", e.target.value)}
                        />
                    </div>
                    <div className="form-group col-md-6">
                        <TextInput
                            name="id_abstract"
                            label="Abstract"
                            value={searchForm.abstract}
                            onChange={e => changeSearchTerm("abstract", e.target.value)}
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
