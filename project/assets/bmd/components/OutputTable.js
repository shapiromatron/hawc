import _ from 'underscore';
import React from 'react';

import {asLabel} from 'bmd/models/bmr';


let getColWidths = function(numBmrs){
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
    },
    binModels = function(models){
        return _.chain(models)
            .groupBy('model_id')
            .values()
            .value();
    };



class OutputTable extends React.Component {

    handleRowClick(id){
        let model = _.findWhere(this.props.models, {id});
        this.props.handleModal(model);
    }

    handleMouseOver(model, evt){
        if (!evt) return;
        evt.stopPropagation();
        evt.nativeEvent.stopImmediatePropagation();
        this.props.handleModelHover(model);
    }

    handleMouseOut(evt){
        if (!evt) return;
        evt.stopPropagation();
        evt.nativeEvent.stopImmediatePropagation();
        this.props.handleModelNoHover();
    }

    renderRow(models){
        let first = models[0],
            bmds = _.chain(models)
                    .map((d)=>{
                        return [
                            <td onMouseOver={this.handleMouseOver.bind(this, d)}
                                onMouseOut={this.handleMouseOut.bind(this)}>{d.output.BMD}</td>,
                            <td onMouseOver={this.handleMouseOver.bind(this)}
                                onMouseOut={this.handleMouseOut.bind(this)}>{d.output.BMDL}</td>,
                        ];
                    })
                    .flatten()
                    .value();

        return (
            <tr key={first.id}
                onMouseOver={this.handleMouseOver.bind(this, first)}
                onMouseOut={this.handleMouseOut.bind(this)}>
                <td>{first.name}</td>
                <td>{first.output.p_value4}</td>
                <td>{first.output.AIC}</td>
                {bmds}
                <td>{first.output.residual_of_interest}</td>
                <td>
                    <button
                        type="button"
                        className='btn btn-link'
                        onClick={this.handleRowClick.bind(this, first.id)}>View</button>
                </td>
            </tr>
        );
    }

    renderHeader(){

        let widths = getColWidths(this.props.bmrs.length),
            ths = _.chain(this.props.bmrs)
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
        if (this.props.models.length ===0){
            return null;
        }

        let binnedModels = binModels(this.props.models);

        return (
            <div className='span8'>
                <table className="table table-condensed table-hover">
                    <thead>
                        {this.renderHeader.bind(this)()}
                    </thead>
                    <tfoot>
                        <tr>
                            <td colSpan="100">
                                Selected model (if any) highlighted in yellow
                            </td>
                        </tr>
                    </tfoot>
                    <tbody style={{cursor: 'pointer'}}>
                    {binnedModels.map(this.renderRow.bind(this))}
                    </tbody>
                </table>
            </div>
        );
    }
}

OutputTable.propTypes = {
    models: React.PropTypes.array.isRequired,
    bmrs: React.PropTypes.array.isRequired,
    handleModal: React.PropTypes.func.isRequired,
    handleModelHover: React.PropTypes.func.isRequired,
    handleModelNoHover: React.PropTypes.func.isRequired,
};

export default OutputTable;
