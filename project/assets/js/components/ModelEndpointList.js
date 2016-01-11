import React, { Component, PropTypes } from 'react';
import fetchEndpointTypes from '../actions';

export default class ModelEndpointList extends Component{
    renderModelItem(item){
        if(item.count == 0){
            return null
        } else {
            return (
                <li key={item.type}>
                    <a href={item.url}>{item.count} {item.type}</a>
                </li>
            );
        }
    }

    render(){
        const { isFetching, items, model } = this.props;

        const isEmpty = (items.reduce( (prev, curr) => prev + curr.count) === 0);
        if(isEmpty){
            return <li><i>No endpoints are available for this {model}.</i></li>

        }
        return (
            <div>
                <h2>{model} Results for Cleanup</h2>
                <ul>
                    {items.map(this.renderModelItem)}
                </ul>
            </div>
        );
    }

}

ModelEndpointList.propTypes = {
    model: PropTypes.string.isRequired,
    items: PropTypes.arrayOf(PropTypes.shape({
        count: PropTypes.number.isRequired,
        type: PropTypes.string.isRequired,
        url: PropTypes.string.isRequired,
    })).isRequired,
};
