import PropTypes from "prop-types";
import React from "react";
import ConfirmDeleteButton from "shared/components/ConfirmDeleteButton";

class EditNodeForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            name: this.props.node.data.name,
            parent: this.props.parent,
        };
    }

    render() {
        const isNew = this.props.node.id === null;
        var deleteText = "Delete this tag";
        if (this.props.node.data.tagCount > 0) {
            if (this.props.node.children) {
                deleteText = `Delete this tag, including its child tags, and all ${this.props.node.data.tagCount} uses of these tags`;
            } else {
                deleteText = `Delete this tag and all ${this.props.node.data.tagCount} uses of this tag`;
            }
        } else if (this.props.node.children) {
            deleteText = `Delete this tag and its ${this.props.node.children.length} child tags`;
        }

        return (
            <div className="editNodeForm container-fluid">
                <div className="row">
                    <div className="form-group col-md-6">
                        <label htmlFor="tag_name" className="col-form-label">
                            Name
                        </label>
                        <div className="form-group form-row">
                            <input
                                name="name"
                                type="text"
                                maxLength="128"
                                className="form-control"
                                onChange={event => this.setState({name: event.target.value})}
                                value={this.state.name}
                            />
                        </div>
                    </div>
                    <div className="form-group col-md-6">
                        <label htmlFor="parent" className="col-form-label">
                            Parent
                        </label>
                        <div className="form-group form-row">
                            <select
                                name="parent"
                                className="form-control"
                                onChange={event => this.setState({parent: event.target.value})}
                                value={this.state.parent}>
                                {this.props.parentOptions.map(d => (
                                    <option key={d[0]} value={d[0]}>
                                        {d[1]}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-6">
                        {isNew ? (
                            <button
                                className="btn btn-primary"
                                onClick={event => {
                                    event.stopPropagation();
                                    this.props.handleCreate(this.state);
                                }}>
                                <i className="fa fa-save"></i>&nbsp;Create
                            </button>
                        ) : (
                            <button
                                className="btn btn-primary"
                                onClick={event => {
                                    event.stopPropagation();
                                    this.props.handleUpdate(this.state);
                                }}>
                                <i className="fa fa-save"></i>&nbsp;Save
                            </button>
                        )}
                        <button
                            onClick={this.props.handleCancel}
                            className="btn btn-secondary ml-2">
                            Cancel
                        </button>
                    </div>

                    {isNew ? null : (
                        <div className="col-md-6">
                            <div className="float-right">
                                <ConfirmDeleteButton
                                    handleDelete={this.props.handleDelete}
                                    deleteText={deleteText}
                                />
                            </div>
                        </div>
                    )}
                </div>
            </div>
        );
    }
}

EditNodeForm.propTypes = {
    parent: PropTypes.number.isRequired,
    node: PropTypes.object.isRequired,
    parentOptions: PropTypes.array.isRequired,
    handleCancel: PropTypes.func.isRequired,
    handleCreate: PropTypes.func,
    handleUpdate: PropTypes.func,
    handleDelete: PropTypes.func,
};

export default EditNodeForm;
