import React, { Component, PropTypes } from 'react';


class List extends Component {
    render() {
        const ComponentToRender = this.props.component;
        let content = (<div></div>);

        if (this.props.items) {
            content = this.props.items.map((item, index) => (
                <ComponentToRender ref={`item-${index}`} key={`item-${index}`} item={item}/>
            ));
        } else {
            content = (<ComponentToRender ref='item' />);
        }

        return (
            <div className='list'>
                {content}
            </div>);
    }
}

List.propTypes = {
    component: PropTypes.func.isRequired,
    items: PropTypes.array,
};

export default List;
