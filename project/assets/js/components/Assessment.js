import React, { Component, PropTypes } from 'react';

export default class Assessment extends Component{
    renderEndpointType(item){
        if(item.count == 0){
            return null;
        } else {
            return (
                <li key={item.type}>
                    <a className="endpoint_type" href={item.url}>{item.count} {item.title}</a>
                </li>
            );
        }
    }

    render() {
        const { items, name } = this.props.object;

        const isEmpty = (items.reduce( (prev, curr) => prev + curr.count) === 0);
        if(isEmpty){
            return <li><i>No endpoints are available for {name}.</i></li>;

        }
        return (
            <div className='assessment'>
                <h2 className='assessment_title'>{name} Results for Cleanup</h2>
                <ul>
                    {items.map(this.renderEndpointType)}
                </ul>
            </div>
        );
    }

}

Assessment.propTypes = {
    object: PropTypes.shape({
        name: PropTypes.string.isRequired,
        items: PropTypes.arrayOf(PropTypes.shape({
            count: PropTypes.number.isRequired,
            type: PropTypes.string.isRequired,
            url: PropTypes.string.isRequired,
        })).isRequired,
    }).isRequired,
};
