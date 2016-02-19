import React, { Component, PropTypes } from 'react';
import { Link } from 'react-router';


class Assessment extends Component{
    renderEndpointType(item){
        if(item.count == 0){
            return null;
        } else {
            return (
                <li key={item.type}>
                    <Link to={item.url}>{item.count} {item.title}</Link>
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
                <h2 className='assessment_title'>Cleanup {name}</h2>
                <p className='help-block'>
                    After data has been initially extracted, this module can be
                    used to update and standardize text which was used during
                    data extraction.
                </p>
                <b>To begin, select a data-type to cleanup</b>
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

export default Assessment;
