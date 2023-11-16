import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import DebugBadge from "shared/components/DebugBadge";
import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class EditRobItem extends Component {
    constructor(props) {
        super(props);
        this.state = {
            authorId: props.rob.author,
            active: props.rob.active,
        };
    }
    render() {
        const {handleCancel, rob, study, store} = this.props;
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
                        helpText="Reassign this review to another person"
                    />
                    <CheckboxInput
                        label="Active"
                        checked={this.state.active}
                        onChange={e => {
                            this.setState({active: e.target.checked});
                        }}
                        helpText="Toggle state (see footnote at bottom of table)"
                    />
                </div>
                <div className="mt-2 d-flex flex-row-reverse">
                    <button
                        className="btn btn-primary mx-1"
                        onClick={() =>
                            store.update(
                                study,
                                rob,
                                {author: this.state.authorId, active: this.state.active},
                                handleCancel
                            )
                        }>
                        <i className="fa fa-fw fa-save"></i>&nbsp;Update
                    </button>
                    <button className="btn btn-secondary mx-1" onClick={handleCancel}>
                        <i className="fa fa-fw fa-times"></i>&nbsp;Cancel
                    </button>
                </div>
            </div>
        );
    }
}
EditRobItem.propTypes = {
    store: PropTypes.object,
    rob: PropTypes.object.isRequired,
    study: PropTypes.object.isRequired,
    handleCancel: PropTypes.func.isRequired,
};

@inject("store")
@observer
class RobItem extends Component {
    constructor(props) {
        super(props);
        this.state = {editForm: false};
    }
    render() {
        const {rob, study} = this.props,
            {editForm} = this.state,
            {edit, user_id, can_edit_assessment} = this.props.store.config,
            activeIcon = rob.active ? "fa fa-fw fa-toggle-on mr-2" : "fa fa-fw fa-toggle-off mr-2",
            activeTitle = rob.active ? "Active" : "Inactive",
            completeIcon = rob.is_complete ? "fa fa-fw fa-check" : "fa fa-fw fa-times",
            completeTitle = rob.is_complete ? "Complete" : "Incomplete",
            showEdit = edit || can_edit_assessment || user_id === rob.author;

        if (editForm) {
            return (
                <EditRobItem
                    rob={rob}
                    study={study}
                    handleCancel={() => this.setState({editForm: false})}
                />
            );
        }

        return (
            <div key={rob.id} className="py-1 clearfix">
                {edit ? <i className={activeIcon} title={activeTitle}></i> : null}
                <span>{rob.author_name}</span>
                {showEdit ? (
                    <a href={rob.edit_url}>
                        <i title="Edit" className="fa fa-fw fa-pencil-square-o"></i>
                    </a>
                ) : null}
                <i className={completeIcon} title={completeTitle}></i>
                {edit ? (
                    <button
                        onClick={() => this.setState({editForm: true})}
                        className="mb-1 float-right btn btn-sm btn-secondary">
                        <i className="fa fa-fw fa-edit"></i>Update
                    </button>
                ) : null}
                <DebugBadge text={rob.id} />
            </div>
        );
    }
}
RobItem.propTypes = {
    store: PropTypes.object,
    rob: PropTypes.object.isRequired,
    study: PropTypes.object.isRequired,
};

export default RobItem;
