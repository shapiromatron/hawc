import React from 'react';
import { connect } from 'react-redux';
import $ from '$';

import DoseResponse from 'bmd/components/DoseResponse';
import ModelOptionTable from 'bmd/components/ModelOptionTable';
import BMROptionTable from 'bmd/components/BMROptionTable';
import ExecuteWell from 'bmd/components/ExecuteWell';
import RecommendationTable from 'bmd/components/RecommendationTable';
import OutputTable from 'bmd/components/OutputTable';


class Tabs extends React.Component {

    componentDidMount(){
        $('#tabs a:first').tab('show');
    }

    handleTabClick(event){
        $(event.currentTarget).tab('show');
    }

    handleExecute(){
        console.log('handled');
    }

    render(){
        let editMode = this.props.config.editMode,
            version = this.props.config.bmds_version;

        return (
            <div>
                <div className="row-fluid">
                    <ul className="nav nav-tabs" id="tabs">
                        <li><a href="#setup"
                            onClick={this.handleTabClick}>BMD setup</a></li>
                        <li><a href="#results"
                            onClick={this.handleTabClick}>Modeling results</a></li>
                        <li><a href="#recommendations"
                            onClick={this.handleTabClick}>Recommendations</a></li>
                    </ul>
                </div>

                <div className="tab-content">
                    <div id="setup" className="tab-pane">
                        <DoseResponse />
                        <h3>Selected models and options</h3>
                        <p>
                            <i>BMDS version: {version}</i>
                        </p>
                        <div className="row-fluid">
                            <ModelOptionTable editMode={editMode} />
                            <BMROptionTable editMode={editMode} />
                        </div>
                        <ExecuteWell
                            editMode={editMode}
                            handleExecute={this.handleExecute.bind(this)} />
                    </div>
                    <div id="results" className="tab-pane">
                        <OutputTable />
                    </div>
                    <div id="recommendations" className="tab-pane">
                        <RecommendationTable />
                    </div>
                </div>

            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        config: state.config,
    };
}

export default connect(mapStateToProps)(Tabs);

