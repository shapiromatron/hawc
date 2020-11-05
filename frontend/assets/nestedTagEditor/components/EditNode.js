import React from "react";
import PropTypes from "prop-types";

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

        return (
            <div className="editNodeForm container-fluid">
                <div className="row">
                    <div className="form-group col-md-6">
                        <label htmlFor="tag_name" className="control-label">
                            Name
                        </label>
                        <div className="controls controls-row">
                            <input
                                name="name"
                                type="text"
                                maxLength="128"
                                className="col-md-12"
                                onChange={event => this.setState({name: event.target.value})}
                                value={this.state.name}
                            />
                        </div>
                    </div>
                    <div className="form-group col-md-6">
                        <label htmlFor="parent" className="control-label">
                            Parent
                        </label>
                        <div className="controls controls-row">
                            <select
                                name="parent"
                                className="col-md-12"
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
                    <div className="well">
                        {isNew ? (
                            <button
                                className="btn btn-primary"
                                onClick={event => {
                                    event.stopPropagation();
                                    this.props.handleCreate(this.state);
                                }}>
                                Create
                            </button>
                        ) : (
                            <button
                                className="btn btn-primary"
                                onClick={event => {
                                    event.stopPropagation();
                                    this.props.handleUpdate(this.state);
                                }}>
                                Save
                            </button>
                        )}
                        <button onClick={this.props.handleCancel} className="btn btn-secondary">
                            Cancel
                        </button>
                        {isNew ? null : (
                            <button
                                className="btn btn-danger float-right"
                                onClick={this.props.handleDelete}>
                                Delete
                            </button>
                        )}
                    </div>
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
