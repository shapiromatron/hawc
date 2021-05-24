import PropTypes from "prop-types";
import React, {Component} from "react";
import Sortable from "sortablejs";
import {observer} from "mobx-react";
import h from "shared/utils/helpers";

const SortableElement = observer(props => {
    const {item, onSelectChange, prefix} = props,
        id = `${prefix}-${item.id}`;
    return (
        <li data-id={item.id} className="list-group-item draggable">
            <button
                type="button"
                className="btn btn-secondary btn-sm draggable-handle mx-2"
                title="Drag to move to preferred location">
                <span className="fa fa-fw fa-arrows-v"></span>
            </button>
            <input
                id={id}
                type="checkbox"
                checked={item.included}
                onChange={e => {
                    e.stopPropagation();
                    onSelectChange(item.id, e.target.checked);
                }}
            />
            <label htmlFor={id}>&nbsp;{item.label}</label>
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
        const {items, onSelectChange} = this.props,
            prefix = h.randomString();
        return (
            <ul className="list-group" ref={this.sortableGroupDecorator}>
                {items.map(item => (
                    <SortableElement
                        key={item.id}
                        item={item}
                        onSelectChange={onSelectChange}
                        prefix={prefix}
                    />
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
            included: PropTypes.bool.isRequired,
        })
    ).isRequired,
    onOrderChange: PropTypes.func.isRequired,
    onSelectChange: PropTypes.func.isRequired,
};
SortableList.defaultProps = {};

export default SortableList;
