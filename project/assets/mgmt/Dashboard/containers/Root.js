import React, { Component } from 'react';
import { connect } from 'react-redux';

class Root extends Component {

  render() {
    return (<div>MyComponent</div>);
  }
}

function mapStateToProps(state){
    return state;
}

export default connect(mapStateToProps)(Root);
