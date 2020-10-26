import React from "react";
import PropTypes from "prop-types";

class EditNode extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            name: this.props.node.data.name,
            parent: this.props.parent,
        };
    }

    onChange(e) {
        let d = {};
        d[e.target.name] = e.target.value;
        this.setState(d);
    }

    handleUpdate(e) {
        e.stopPropagation();
        this.props.handleUpdate(this.state);
    }

    handleCreate(e) {
        e.stopPropagation();
        this.props.handleCreate(this.state);
    }

    renderUpdateWell() {
        return (
            <div className="well">
                <button className="btn btn-primary" onClick={this.handleUpdate.bind(this)}>
                    Save
                </button>
                <button onClick={this.props.handleCancel} className="btn btn-default">
                    Cancel
                </button>
                <button className="btn btn-danger pull-right" onClick={this.props.handleDelete}>
                    Delete
                </button>
            </div>
        );
    }

    renderCreateWell() {
        return (
            <div className="well">
                <button className="btn btn-primary" onClick={this.handleCreate.bind(this)}>
                    Create
                </button>
                <button onClick={this.props.handleCancel} className="btn btn-default">
                    Cancel
                </button>
            </div>
        );
    }

    render() {
        let well = this.props.node.id === null ? this.renderCreateWell : this.renderUpdateWell;

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
                                onChange={this.onChange.bind(this)}
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
                                onChange={this.onChange.bind(this)}
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

                <div className="row">{well.bind(this)()}</div>
            </div>
        );
    }
}

EditNode.propTypes = {
    parent: PropTypes.number.isRequired,
    node: PropTypes.object.isRequired,
    parentOptions: PropTypes.array.isRequired,
    handleCancel: PropTypes.func.isRequired,
    handleCreate: PropTypes.func,
    handleUpdate: PropTypes.func,
    handleDelete: PropTypes.func,
};

export default EditNode;
