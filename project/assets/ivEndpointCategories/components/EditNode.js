import React from 'react';

class EditNode extends React.Component {

    render() {
        let node = (this.props.node)?
            this.props.node.data:
            {};

        return (
            <div>

                <div className="control-group form-row">
                    <label htmlFor="tag_name" className="control-label">Name</label>
                    <div className="controls">
                        <input id="tag_name" type="text" maxLength="128" value={node.name} />
                    </div>
                </div>

                <div className="control-group form-row">
                    <label htmlFor="tag_name" className="control-label">Nest under</label>
                    <div className="controls">
                        <select>
                            <option>{this.props.parent.data.name}</option>
                        </select>
                    </div>
                </div>

                <div className="well">
                    <button
                        className="btn btn-primary">Save</button>
                    <button
                        onClick={this.props.handleCancel}
                        className="btn btn-default">Cancel</button>
                    <button
                        className="btn btn-danger pull-right">Delete</button>
                </div>
            </div>
        );
    }
}

EditNode.propTypes = {
    node: React.PropTypes.object,
    parent: React.PropTypes.object,
    handleCancel: React.PropTypes.func.isRequired,
    handleSave: React.PropTypes.func.isRequired,
    handleDelete: React.PropTypes.func.isRequired,
};

export default EditNode;
