import React from 'react';
import { Provider } from 'react-redux';
import $ from 'jQuery';

import { loadConfig } from 'shared/actions/Config';


class Root extends React.Component {

    componentWillMount(){
        this.props.store.dispatch(loadConfig());
    }

    componentDidMount(){
        $('#tabs a:first').tab('show');
    }

    handleTabClick(event){
        $(event.currentTarget).tab('show');
    }

    renderDoseResponse(){
        return (
            <div>
                <h3>Dose-response</h3>
                <div className="row-fluid">
                    <div className="span8">
                        <p>Table</p>
                        <table className="table table-condensed table-striped">
                        </table>

                        <button type='button' onClick={this.handleShowOptionModal.bind(this)}>Model</button>
                        <button type='button' onClick={this.handleShowBMRModal.bind(this)}>BMR</button>
                        <button type='button' onClick={this.handleShowOutputModal.bind(this)}>Output</button>

                    </div>
                    <div className="span4">
                        <p>Figure</p>
                    </div>
                </div>
            </div>
        );
    }

    renderModelOptions(){
        let header = (this.props.store.getState().config.editMode)?
             'View/edit': 'View';
        return (
            <div className="span6">
                <h4>Model options</h4>
                <table className="table table-condensed table-striped">
                    <thead>
                        <tr>
                            <th style={{width: '30%'}}>Model name</th>
                            <th style={{width: '60%'}}>Non-default settings</th>
                            <th style={{width: '10%'}}>{header}</th>
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            </div>
        );
    }

    renderBMROptions(){
        let header = (this.props.store.getState().config.editMode)?
             'View/edit': 'View';
        return (
            <div className="span6">
                <h4>Benchmark modeling responses</h4>
                <table className="table table-condensed table-striped">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Value</th>
                            <th>Confidence level</th>
                            <th style={{width:'10%'}}>{header}</th>
                        </tr>
                    </thead>
                    <tfoot>
                        <tr>
                            <td colSpan="4">
                            All models will be run using the selected BMRs,
                            if appropriate for that particular model type.
                            </td>
                        </tr>
                    </tfoot>
                    <tbody>
                    </tbody>
                </table>
            </div>
        );
    }

    renderSetup(){
        let version = '2.6.0.1';
        return (
            <div>
                {this.renderDoseResponse()}

                <h3>Selected models and options</h3>
                <p>
                    <i>BMDS version: {version}</i>
                </p>

                <div className="row-fluid">
                    {this.renderModelOptions()}
                    {this.renderBMROptions()}
                </div>

                <div className='well'>
                    <a className='btn btn-primary'>Execute</a>
                </div>

           </div>
        );
    }

    renderResults(){
        return (
            <div>
                <h3>BMDS output summary</h3>
                <div className="row-fluid">

                    <div className='span8'>
                        <table className="table table-condensed">
                            <thead>
                            </thead>
                            <tfoot>
                                <tr>
                                    <td colSpan="100">
                                        Selected model highlighted in yellow
                                    </td>
                                </tr>
                            </tfoot>
                            <tbody>
                            </tbody>
                        </table>
                    </div>

                    <div className='d3_container span4'>
                    </div>

                </div>
            </div>
        );
    }

    renderRecommendations(){
        return (
            <table className="table table-striped table-condensed">
                <thead>
                    <tr>
                        <th style={{width: '20%'}}>Description</th>
                        <th style={{width: '70%'}}>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Model</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>Override</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>Notes</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        );
    }

    renderTabs(){
        return (
            <div>
                <div className="row-fluid">
                    <ul className="nav nav-tabs" id="tabs">
                        <li><a href="#setup" onClick={this.handleTabClick}>BMD setup</a></li>
                        <li><a href="#results" onClick={this.handleTabClick}>Modeling results</a></li>
                        <li><a href="#recommendations" onClick={this.handleTabClick}>Recommendations</a></li>
                    </ul>
                </div>

                <div className="tab-content">
                    <div id="setup" className="tab-pane">
                        {this.renderSetup()}
                    </div>
                    <div id="results" className="tab-pane">
                        {this.renderResults()}
                    </div>
                    <div id="recommendations" className="tab-pane">
                        {this.renderRecommendations()}
                    </div>
                </div>

            </div>
        );
    }

    renderOptionModal(){
        let modelName = 'Multistage';
        return (
            <div className="modal hide fade" ref='optionModal'>

                <div className="modal-header">
                    <button className="close" type="button" data-dismiss="modal">×</button>
                    <h3>{modelName} model options</h3>
                </div>

                <div className="modal-body">

                    <div className='row-fluid'>
                        <div className='span6'>
                            <h4>Model settings</h4>
                            <table className="table table-condensed table-striped">
                            </table>
                        </div>

                        <div className='span6'>
                            <h4>Optimization</h4>
                            <table className="table table-condensed table-striped">
                            </table>
                        </div>
                    </div>

                    <div className='row-fluid'>
                        <h4>Parameter assignment</h4>
                        <table className="table table-condensed table-striped">
                        </table>
                    </div>

                </div>

                <div className="modal-footer">
                    <button type='button'
                        className='btn btn-primary'
                        data-dismiss='modal'>Close</button>
                </div>
            </div>
        );
    }

    renderBMRModal(){
        return (
            <div className="modal hide fade" role="dialog" ref='bmrModal'>

                <div className="modal-header">
                    <button className="close" type="button"
                        data-dismiss="modal">×</button>
                    <h3>Benchmark response</h3>
                </div>

                <div className="modal-body">
                    <table className="table table-condensed table-striped">
                        <tbody>
                            <tr>
                                <th style={{width: '50%'}}>BMR type</th>
                                <td style={{width: '50%'}}></td>
                            </tr>
                            <tr>
                                <th>Value</th>
                                <td></td>
                            </tr>
                            <tr>
                                <th>Confidence level</th>
                                <td></td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div className="modal-footer">
                    <button className='btn btn-primary'
                        data-dismiss="modal">Close</button>
                </div>
            </div>
        );
    }

    renderOutputModal(){
        var modelName = 'Multistage';
        return (
            <div className="modal hide fade" tabindex="-1" ref='outputModal' role="dialog">

                <div className="modal-header">
                    <button className="close" type="button" data-dismiss="modal">×</button>
                    <h3>{modelName} model output</h3>
                </div>

                <div className="modal-body">
                    <pre></pre>
                </div>

                <div className="modal-footer">
                    <button type='button'
                        className='btn btn-primary'
                        data-dismiss='modal'>Close</button>
                </div>

            </div>
        );
    }

    handleShowOptionModal(){
        $(this.refs.optionModal).modal('show');
    }

    handleShowBMRModal(){
        $(this.refs.bmrModal).modal('show');
    }

    handleShowOutputModal(){
        $(this.refs.outputModal).modal('show');
    }

    render() {
        let store = this.props.store;
        return (
            <Provider store={store}>
                <div>
                {this.renderTabs()}
                {this.renderOutputModal()}
                {this.renderOptionModal()}
                {this.renderBMRModal()}
                </div>
            </Provider>
        );
    }
}

Root.propTypes = {
    store: React.PropTypes.object.isRequired,
};

export default Root;
