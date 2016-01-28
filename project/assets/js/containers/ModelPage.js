import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';

function loadData(props){
    const { assessment_id } = props;
    props.loadModel(assessment_id);
}

class ModelPage extends Component {
    constructor(props){
        super(props);
        this.render;
    }
}
