import React from 'react';


class OutputTable extends React.Component {

    handleRowClick(i, d){
        this.props.handleModal(this.props.models[i].outfile);
    }

    render() {
        return (
            <div>
                <h3>BMDS output summary</h3>
                <div className="row-fluid">

                    <div className='span8'>
                        <table className="table table-condensed">
                            <thead>
                                <tr>
                                    <th>Model</th>
                                    <th>Global <i>p</i>-value</th>
                                    <th>AIC</th>
                                    <th>BMD</th>
                                    <th>BMDL</th>
                                    <th>Residual of interest</th>
                                    <th>Output</th>
                                </tr>
                            </thead>
                            <tfoot>
                                <tr>
                                    <td colSpan="100">
                                        Selected model highlighted in yellow
                                    </td>
                                </tr>
                            </tfoot>
                            <tbody>
                            {this.props.models.map((d, i)=>{
                                return (
                                    <tr key={i}>
                                        <td>{d.name}</td>
                                        <td>{d.output.p_value4}</td>
                                        <td>{d.output.AIC}</td>
                                        <td>{d.output.BMD}</td>
                                        <td>{d.output.BMDL}</td>
                                        <td>{d.output.residual_of_interest}</td>
                                        <td>
                                            <button
                                                type="button"
                                                className='btn btn-link'
                                                onClick={this.handleRowClick.bind(this, i)}>View</button>
                                        </td>
                                    </tr>
                                );
                            })}
                            </tbody>
                        </table>
                    </div>

                    <div className='d3_container span4'>
                    </div>

                </div>
            </div>
        );
    }
}

OutputTable.propTypes = {
    models: React.PropTypes.array.isRequired,
    handleModal: React.PropTypes.func.isRequired,
};

export default OutputTable;
