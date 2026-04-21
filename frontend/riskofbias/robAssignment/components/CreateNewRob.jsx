import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class CreateNewRob extends Component {
    constructor(props) {
        super(props);
        this.state = {
            editForm: false,
            authorId: props.store.defaultAuthorId,
        };
    }
    renderUpdate() {
        const {store, study, final} = this.props,
            {authorId} = this.state;
        return (
            <div className="well">
                <div>
                    <SelectInput
                        label="Author"
                        choices={store.authorOptions}
                        value={authorId}
                        handleSelect={value => {
                            this.setState({authorId: value});
                        }}
                    />
                </div>
                <div className="mt-2 d-flex flex-row-reverse">
                    <button
                        className="btn btn-primary mx-1"
                        onClick={() =>
                            store.create(study, this.state.authorId, final, () => {
                                this.setState({editForm: false});
                            })
                        }>
                        <i className="fa fa-fw fa-save"></i>Create
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
        return (
            <div className="clearfix">
                <button
                    onClick={() => this.setState({editForm: true})}
                    className="mb-1 float-right btn btn-sm btn-primary">
                    <i className="fa fa-fw fa-plus"></i>Create
                </button>
            </div>
        );
    }
    render() {
        const {editForm} = this.state;
        return editForm ? this.renderUpdate() : this.renderRead();
    }
}
CreateNewRob.propTypes = {
    store: PropTypes.object,
    study: PropTypes.object.isRequired,
    final: PropTypes.bool.isRequired,
};

export default CreateNewRob;
