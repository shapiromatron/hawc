import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Loading from "shared/components/Loading";

@inject("store")
@observer
class ReferenceSearchMain extends Component {
    render() {
        const {store} = this.props;

        return (
            <div className="row-fluid">
                <div className="accordion" id="searchFormAccordion">
                    <div className="accordion-group">
                        <div className="accordion-heading">
                            <a
                                className="accordion-toggle"
                                data-toggle="collapse"
                                data-parent="#searchFormAccordion"
                                href="#searchCollapser">
                                Search settings
                            </a>
                        </div>
                        <div id="searchCollapser" className="accordion-body collapse in">
                            <div className="accordion-inner container-fluid">
                                <div className="control-group">
                                    <label htmlFor="id_db_id" className="control-label">
                                        Database unique identifier
                                    </label>
                                    <div className="controls">
                                        <input
                                            type="number"
                                            id="id_db_id"
                                            onChange={e => {
                                                store.changeSearchTerm(
                                                    "db_id",
                                                    parseInt(e.target.value)
                                                );
                                            }}
                                        />
                                        <p className="help-block">
                                            Identifiers may include Pubmed ID, DOI, etc.
                                        </p>
                                    </div>
                                </div>
                                <div className="well">
                                    <button className="btn btn-primary" onClick={store.search}>
                                        <i className="fa fa-search"></i>&nbsp;Search
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div>
                    <Loading />
                    <p>results div</p>
                </div>
            </div>
        );
    }
}

ReferenceSearchMain.propTypes = {
    store: PropTypes.object,
};

export default ReferenceSearchMain;
