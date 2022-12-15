import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import EditForm from "./EditForm";

@inject("store")
@observer
class EditContainer extends Component {
    render() {
        const {store} = this.props;
        if (store.isConfirmDelete) {
            return (
                <div className="alert alert-danger">
                    <p>Are you sure you want to delete this text?</p>
                    <div className="well">
                        <button className="btn btn-danger" onClick={store.deleteItem}>
                            <i className="fa fa-fw fa-trash"></i>&nbsp;Delete
                        </button>
                        <button className="btn btn-light mx-2" onClick={store.cancelConfirmDelete}>
                            Cancel
                        </button>
                    </div>
                </div>
            );
        }

        if (store.isEditing) {
            return (
                <>
                    <EditForm />
                    {store.selectedId ? (
                        <div className="well">
                            <button className="btn btn-primary" onClick={store.createOrUpdate}>
                                <i className="fa fa-fw fa-edit"></i>&nbsp;Update
                            </button>
                            <button className="btn btn-light mx-2" onClick={store.cancelEditing}>
                                Cancel
                            </button>
                            <button
                                className="btn btn-danger float-right"
                                onClick={store.clickConfirmDelete}>
                                <i className="fa fa-fw fa-trash"></i>&nbsp;Delete
                            </button>
                        </div>
                    ) : null}
                    {store.isCreating ? (
                        <div className="well">
                            <button className="btn btn-primary" onClick={store.createOrUpdate}>
                                <i className="fa fa-fw fa-save"></i>&nbsp;Create
                            </button>

                            <button className="btn btn-light mx-2" onClick={store.cancelEditing}>
                                Cancel
                            </button>
                        </div>
                    ) : null}
                </>
            );
        }

        return <p>Please create a new item or edit an existing.</p>;
    }
}

EditContainer.propTypes = {
    store: PropTypes.object,
};

export default EditContainer;
