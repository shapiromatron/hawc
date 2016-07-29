import React from 'react';

class EditNode extends React.Component {

    componentWillMount(){
        this.setState({
            name: this.props.node.data.name,
        });
    }

    onChange(e){
        let d = {};
        d[e.target.name] = e.target.value;
        this.setState(d);
    }

    render() {
        return (
            <div className="editNodeForm container-fluid" >
                <div className="row-fluid">
                    <div className="control-group span12">
                        <label htmlFor="tag_name" className="control-label">Name</label>
                        <div className="controls">
                            <input name="name" type="text" maxLength="128"
                                onChange={this.onChange.bind(this)} value={this.state.name} />
                        </div>
                    </div>
                </div>

                <div className='row-fluid'>
                    <div className="well">
                        <button
                            className="btn btn-primary"
                            onClick={this.props.handleSave}
                            >Save</button>
                        <button
                            onClick={this.props.handleCancel}
                            className="btn btn-default">Cancel</button>
                        <button
                            className="btn btn-danger pull-right"
                            onClick={this.props.handleDelete}
                            >Delete</button>
                    </div>
                </div>
            </div>
        );
    }
}

EditNode.propTypes = {
    parent: React.PropTypes.object,
    node: React.PropTypes.object.isRequired,
    handleCancel: React.PropTypes.func.isRequired,
    handleSave: React.PropTypes.func.isRequired,
    handleDelete: React.PropTypes.func.isRequired,
};

export default EditNode;
