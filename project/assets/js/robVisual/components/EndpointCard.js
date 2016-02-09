import React, { Component } from 'react';
import _ from 'underscore';

export default class EndpointCard extends Component {
    render(){
        return (
            <div className='span3'>
                {this.props.d}
                <h4>Endpoint name<br/>(with link to endpoint)</h4>
                <p>Dose-response plot placeholder</p>
                <p>Extra content text here...</p>
                <button type='button' className='btn btn-default'>Show detail modal</button>
            </div>
        );
    }
}
