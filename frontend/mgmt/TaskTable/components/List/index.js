import React, {Component} from "react";
import PropTypes from "prop-types";

class List extends Component {
    render() {
        const {component, items, ...rest} = this.props,
            ComponentToRender = component;
        let content = <div />;

        this.components = [];

        if (items) {
            content = this.props.items.map((item, index) => (
                <ComponentToRender
                    ref={c => this.components.push(c)}
                    key={`item-${index}`}
                    item={item}
                    {...rest}
                />
            ));
        } else {
            content = <ComponentToRender ref={c => this.components.push(c)} {...rest} />;
        }

        return <div className="list">{content}</div>;
    }
}

List.propTypes = {
    component: PropTypes.func.isRequired,
    items: PropTypes.array,
};

export default List;
