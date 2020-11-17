import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

@inject("store")
@observer
class SearchForm extends Component {
    render() {
        const {changeSearchTerm, submitSearch, resetForm} = this.props.store;

        return (
            <form>
                <div className="row">
                    <div className="form-group col-md-4">
                        <label htmlFor="id_hawc_id" className="control-label">
                            HAWC ID
                        </label>
                        <div className="form-group">
                            <input
                                className="form-control"
                                type="number"
                                id="id_hawc_id"
                                onChange={e => changeSearchTerm("id", parseInt(e.target.value))}
                            />
                        </div>
                    </div>
                    <div className="form-group col-md-4">
                        <label htmlFor="id_db_id" className="control-label">
                            Database unique identifier
                        </label>
                        <div className="form-group">
                            <input
                                className="form-control"
                                type="number"
                                id="id_db_id"
                                onChange={e => changeSearchTerm("db_id", parseInt(e.target.value))}
                            />
                            <p className="help-block">
                                Identifiers may include Pubmed ID, DOI, etc.
                            </p>
                        </div>
                    </div>
                    <div className="form-group col-md-4">
                        <label htmlFor="id_year_id" className="control-label">
                            Year
                        </label>
                        <div className="form-group">
                            <input
                                className="form-control"
                                type="number"
                                id="id_year_id"
                                onChange={e => changeSearchTerm("year", parseInt(e.target.value))}
                            />
                        </div>
                    </div>
                </div>
                <div className="row">
                    <div className="form-group col-md-6">
                        <label htmlFor="id_title" className="control-label">
                            Title
                        </label>
                        <div className="form-group">
                            <input
                                className="form-control"
                                type="text"
                                id="id_title"
                                onChange={e => changeSearchTerm("title", e.target.value)}
                            />
                        </div>
                    </div>
                    <div className="form-group col-md-6">
                        <label htmlFor="id_authors" className="control-label">
                            Authors
                        </label>
                        <div className="form-group">
                            <input
                                className="form-control"
                                type="text"
                                id="id_authors"
                                onChange={e => changeSearchTerm("authors", e.target.value)}
                            />
                        </div>
                    </div>
                </div>
                <div className="row">
                    <div className="form-group col-md-6">
                        <label htmlFor="id_journal" className="control-label">
                            Journal
                        </label>
                        <div className="form-group">
                            <input
                                className="form-control"
                                type="text"
                                id="id_journal"
                                onChange={e => changeSearchTerm("journal", e.target.value)}
                            />
                        </div>
                    </div>
                    <div className="form-group col-md-6">
                        <label htmlFor="id_abstract" className="control-label">
                            Abstract
                        </label>
                        <div className="form-group">
                            <input
                                className="form-control"
                                type="text"
                                id="id_abstract"
                                onChange={e => changeSearchTerm("abstract", e.target.value)}
                            />
                        </div>
                    </div>
                </div>
                <div className="well">
                    <button
                        className="btn btn-primary"
                        type="button"
                        onClick={() => submitSearch()}>
                        <i className="fa fa-search"></i>&nbsp;Search
                    </button>
                    <span>&nbsp;</span>
                    <button className="btn btn-light" type="button" onClick={() => resetForm()}>
                        Reset
                    </button>
                </div>
            </form>
        );
    }
}

SearchForm.propTypes = {
    store: PropTypes.object,
};

export default SearchForm;
