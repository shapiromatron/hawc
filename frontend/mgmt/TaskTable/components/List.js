import React, {Component} from "react";
import PropTypes from "prop-types";

class List extends Component {
    render() {
        const {component, items, ...props} = this.props,
            ComponentToRender = component;
        let content = <div />;

        this.components = [];

        if (items) {
            content = items.map((item, index) => (
                <ComponentToRender
                    ref={c => this.components.push(c)}
                    key={`item-${index}`}
                    item={item}
                    {...props}
                />
            ));
        } else {
            content = <ComponentToRender ref={c => this.components.push(c)} {...props} />;
        }

        return <div className="list">{content}</div>;
    }
}

List.propTypes = {
    component: PropTypes.func.isRequired,
    items: PropTypes.array,
};

export default List;
