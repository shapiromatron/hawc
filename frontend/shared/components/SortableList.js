import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Sortable from "sortablejs";

const SortableElement = observer(props => {
    const {item} = props;
    return (
        <li data-id={item.id} className="list-group-item draggable py-2">
            <button
                type="button"
                className="btn btn-secondary btn-sm draggable-handle mx-2"
                title="Drag to move to preferred location">
                <span className="fa fa-fw fa-arrows-v"></span>
            </button>
            <label>{item.label}</label>
        </li>
    );
});

@observer
class SortableList extends Component {
    constructor(props) {
        super(props);

        this.sortableGroupDecorator = componentBackingInstance => {
            if (!componentBackingInstance) {
                return;
            }
            Sortable.create(componentBackingInstance, {
                draggable: ".draggable",
                ghostClass: "draggable-ghost",
                handle: ".draggable-handle",
                animation: 200,
                onUpdate: e => {
                    props.onOrderChange(parseInt(e.item.dataset.id), e.oldIndex, e.newIndex);
                },
            });
        };
    }
    render() {
        const {items} = this.props;
        return (
            <ul className="list-group" ref={this.sortableGroupDecorator}>
                {items.map(item => (
                    <SortableElement key={item.id} item={item} />
                ))}
            </ul>
        );
    }
}

SortableList.propTypes = {
    items: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.any.isRequired,
            label: PropTypes.string.isRequired,
        })
    ).isRequired,
    onOrderChange: PropTypes.func.isRequired,
};
SortableList.defaultProps = {};

export default SortableList;
