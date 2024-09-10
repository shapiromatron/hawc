import PropTypes from "prop-types";
import React, {Component} from "react";

class DssToxDetailTable extends Component {
    render() {
        const {showHeader} = this.props,
            {data} = this.props.object;
        return (
            <div className="container-fluid">
                {showHeader ? (
                    <div className="row">
                        <h3>Substance information</h3>
                    </div>
                ) : null}
                <div className="row">
                    <table className="table table-sm">
                        <tbody>
                            <tr>
                                <td rowSpan={5}>
                                    <a href={data.image_url}>
                                        <img
                                            alt="chemical structure image"
                                            style={{width: 150}}
                                            src={data.image_url}
                                        />
                                    </a>
                                </td>
                                <th>Common name</th>
                                <td>{data.content.preferredName}</td>
                            </tr>
                            <tr>
                                <th>DTXSID</th>
                                <td>
                                    <a href={data.dashboard_url}>{data.content.dtxsid}</a>
                                </td>
                            </tr>
                            <tr>
                                <th>CASRN</th>
                                <td>{data.content.casrn}</td>
                            </tr>
                            <tr>
                                <th>SMILES</th>
                                <td>{data.content.smiles}</td>
                            </tr>
                            <tr>
                                <th>Molecular weight</th>
                                <td>{data.content.molWeight}</td>
                            </tr>
                        </tbody>
                        <tfoot>
                            <tr>
                                <td style={{borderTop: "0px"}}>&nbsp;</td>
                                <td colSpan={2}>
                                    <p className="form-text text-muted">
                                        Chemical information provided by&nbsp;
                                        <a href="https://comptox.epa.gov/dashboard/">
                                            USEPA Chemicals Dashboard
                                        </a>
                                    </p>
                                </td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
        );
    }
}

DssToxDetailTable.propTypes = {
    object: PropTypes.object.isRequired,
    showHeader: PropTypes.bool.isRequired,
};

export default DssToxDetailTable;
