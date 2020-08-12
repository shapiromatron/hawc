import React, {Component} from "react";
import ReactDOM from "react-dom";
import PropTypes from "prop-types";

class ChemicalDetail extends Component {
    render() {
        const {content, showHeader} = this.props;
        return (
            <div>
                {showHeader ? <h3>Chemical Properties Information</h3> : null}
                <ul>
                    <li>
                        <b>Common name:</b>&nbsp;{content.preferredName}
                    </li>
                    <li>
                        <b>CASRN:</b>&nbsp;{content.casrn}
                    </li>
                    <li>
                        <b>DTXSID:</b>&nbsp;
                        <a href={content.url_dashboard}>{content.dtxsid}</a>
                    </li>
                    <li>
                        <b>SMILES:</b>&nbsp;{content.smiles}
                    </li>
                    <li>
                        <b>Molecular Weight:</b>&nbsp;{content.molWeight}
                    </li>
                    <li>
                        <img src={`data:image/jpeg;base64,${content.image}`} />
                    </li>
                </ul>
                <p className="help-block">
                    Chemical information provided by&nbsp;
                    <a href="https://comptox.epa.gov/dashboard/">USEPA Chemicals Dashboard</a>
                </p>
            </div>
        );
    }
}

ChemicalDetail.propTypes = {
    content: PropTypes.object.isRequired,
    showHeader: PropTypes.bool.isRequired,
};

const renderChemicalDetails = function(el, content, showHeader) {
    ReactDOM.render(<ChemicalDetail content={content} showHeader={showHeader} />, el);
};

export default renderChemicalDetails;
