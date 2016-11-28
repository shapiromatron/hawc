import React, { Component, PropTypes } from 'react';


class List extends Component {
    render() {
        const { component, items, ...rest } = this.props,
            ComponentToRender = component;
        let content = (<div></div>);

        if (items) {
            content = this.props.items.map((item, index) => (
                <ComponentToRender ref={`item-${index}`} key={`item-${index}`} item={item} {...rest} />
            ));
        } else {
            content = (<ComponentToRender ref='item' {...rest} />);
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
