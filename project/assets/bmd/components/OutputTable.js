import React from 'react';

import {asLabel} from 'bmd/models/bmr';


class OutputTable extends React.Component {

    handleRowClick(i, d){
        this.props.handleModal(this.props.models[i]);
    }

    renderRow(d, i){
        let {bmrs} = this.props;

        return (
            <tr key={d.id}>
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
    }

    renderHeader(){

        let widths = function(numBmrs){
            switch(numBmrs){
            case 1:
                return {
                    name: '20%',
                    nums: '14%',
                    view: '10%',
                };
            case 2:
                return {
                    name: '16%',
                    nums: '11%',
                    view: '7%',
                };
            case 3:
                return {
                    name: '12%',
                    nums: '9%',
                    view: '7%',
                };
            default:
                return {
                    name: '1%',
                    nums: '1%',
                    view: '1%',
                };
            }
        }(this.props.bmrs.length);

        let ths = _.chain(this.props.bmrs)
                .map((d)=>{
                    let lbl = asLabel(d);
                    return [
                        <th style={{width: widths.nums}}>BMD<br/><span>({lbl})</span></th>,
                        <th style={{width: widths.nums}}>BMDL<br/><span>({lbl})</span></th>,
                    ];
                })
                .flatten()
                .value();

        return (
            <tr>
                <th style={{width: widths.name}}>Model</th>
                <th style={{width: widths.nums}}>Global <br /><i>p</i>-value</th>
                <th style={{width: widths.nums}}>AIC</th>
                {ths}
                <th style={{width: widths.nums}}>Residual of interest</th>
                <th style={{width: widths.view}}>Output</th>
            </tr>
        );
    }

    render() {
        return (
            <div>
                <h3>BMDS output summary</h3>
                <div className="row-fluid">

                    <div className='span8'>
                        <table className="table table-condensed">
                            <thead>
                                {this.renderHeader.bind(this)()}
                            </thead>
                            <tfoot>
                                <tr>
                                    <td colSpan="100">
                                        Selected model highlighted in yellow
                                    </td>
                                </tr>
                            </tfoot>
                            <tbody>
                            {this.props.models.map(this.renderRow.bind(this))}
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
    bmrs: React.PropTypes.array.isRequired,
    handleModal: React.PropTypes.func.isRequired,
};

export default OutputTable;
