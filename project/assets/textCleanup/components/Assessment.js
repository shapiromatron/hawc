import React, { Component, PropTypes } from 'react';
import { Link } from 'react-router';


class Assessment extends Component{

    renderItemType(item){
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
        const { object, helpText } = this.props;

        const isEmpty = (object.items.reduce( (prev, curr) => prev + curr.count) === 0);
        if(isEmpty){
            return <li><i>No items are available for {object.name}.</i></li>;

        }
        return (
            <div className='assessment'>
                <h2 className='assessment_title'>Cleanup {object.name}</h2>
                <p className='help-block'>
                    {helpText}
                </p>
                <b>To begin, select a data-type to cleanup</b>
                <ul>
                    {object.items.map(this.renderItemType)}
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
    helpText: PropTypes.string.isRequired,
};

export default Assessment;
