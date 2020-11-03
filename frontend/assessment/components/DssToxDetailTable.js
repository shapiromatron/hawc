import React, {Component} from "react";
import PropTypes from "prop-types";

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
                                <td rowSpan={5} style={{borderTop: "0px"}}>
                                    <img
                                        style={{minWidth: 150, minHeight: 150}}
                                        src={data.svg_url}
                                    />
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
                                    <p className="help-block">
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
