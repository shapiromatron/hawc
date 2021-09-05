import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

import SelectInput from "shared/components/SelectInput";
import CheckboxInput from "shared/components/CheckboxInput";

@inject("store")
@observer
class RobItem extends Component {
    constructor(props) {
        super(props);
        this.state = {
            editForm: false,
            authorId: props.rob.author,
            active: props.rob.active,
        };
    }
    renderUpdate() {
        const {rob, store} = this.props;
        return (
            <div key={rob.id} className="well">
                <div>
                    <SelectInput
                        label="Author"
                        choices={store.authorOptions}
                        value={this.state.authorId}
                        handleSelect={value => {
                            this.setState({authorId: value});
                        }}
                    />
                    <CheckboxInput
                        label="Active"
                        checked={this.state.active}
                        onChange={e => {
                            this.setState({active: e.target.checked});
                        }}
                    />
                </div>
                <div className="mt-2 d-flex flex-row-reverse">
                    <button
                        className="btn btn-primary mx-1"
                        onClick={() =>
                            store.update(
                                rob,
                                {author: this.state.authorId, active: this.state.active},
                                () => {
                                    this.setState({editForm: false});
                                }
                            )
                        }>
                        <i className="fa fa-fw fa-save"></i>&nbsp;Update
                    </button>
                    <button
                        className="btn btn-secondary mx-1"
                        onClick={() => this.setState({editForm: false})}>
                        <i className="fa fa-fw fa-times"></i>&nbsp;Cancel
                    </button>
                </div>
            </div>
        );
    }
    renderRead() {
        const {rob} = this.props,
            activeIcon = rob.active ? "fa fa-fw fa-toggle-on mr-2" : "fa fa-fw fa-toggle-off mr-2",
            activeTitle = rob.active ? "active" : "inactive";
        return (
            <div key={rob.id} className="clearfix">
                <i className={activeIcon} title={activeTitle}></i>
                {rob.author_name}
                <button
                    onClick={() => this.setState({editForm: true})}
                    className="mb-1 pull-right btn btn-secondary">
                    <i className="fa fa-fw fa-edit"></i>Edit
                </button>
            </div>
        );
    }
    render() {
        const {editForm} = this.state;
        return editForm ? this.renderUpdate() : this.renderRead();
    }
}
RobItem.propTypes = {
    store: PropTypes.object,
    rob: PropTypes.object.isRequired,
};

export default RobItem;
