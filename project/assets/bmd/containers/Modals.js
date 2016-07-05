import React from 'react';
import { connect } from 'react-redux';

import ModelOptionModal from 'bmd/components/ModelOptionModal';
import BMROptionModal from 'bmd/components/BMROptionModal';
import OutputModal from 'bmd/components/OutputModal';

import {
    showOptionModal,
    showBMRModal,
    showOutputModal,
} from 'bmd/actions';


class Modals extends React.Component {

    handleOptionClick(){
        this.props.dispatch(showOptionModal);
    }

    handleBMRClick(){
        this.props.dispatch(showBMRModal);
    }

    handleOutputClick(){
        this.props.dispatch(showOutputModal);
    }


    render() {
        let {editMode} = this.props.config;
        return (
            <div>

                <ModelOptionModal editMode={editMode} />
                <BMROptionModal editMode={editMode} />
                <OutputModal />

                <button type='button'
                    onClick={this.handleOptionClick.bind(this)}>Model</button>
                <button type='button'
                    onClick={this.handleBMRClick.bind(this)}>BMR</button>
                <button type='button'
                    onClick={this.handleOutputClick.bind(this)}>Output</button>
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        config: state.config,
    };
}

export default connect(mapStateToProps)(Modals);

