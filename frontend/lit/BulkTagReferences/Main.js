import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";
import {toJS} from "mobx";
import _ from "lodash";

import Reference from "../components/Reference";
import TagTree from "../components/TagTree";

@inject("store")
@observer
class BulkTagReferencesMain extends Component {
    render() {
        const {store} = this.props,
            {handleFileInput} = store;
        return (
            <div>
                <button onClick={store.getReferences}>Get references</button>
                <button onClick={store.getTags}>Get tags</button>
                <input id="fileItem" type="file" onChange={handleFileInput} />
                Pick id column
                <select onChange={e => store.setDatasetIdColumn(e.target.value)}>
                    {_.map(store.datasetColumnChoices, c => (
                        <option value={c[0]}>{c[1]}</option>
                    ))}
                </select>
                Pick id column type
                <select onChange={e => store.setReferenceIdColumn(e.target.value)}>
                    {_.map(store.referenceColumnChoices, c => (
                        <option value={c[0]}>{c[1]}</option>
                    ))}
                </select>
                Pick tag column
                <select onChange={e => store.setDatasetTagColumn(e.target.value)}>
                    {_.map(store.datasetColumnChoices, c => (
                        <option value={c[0]}>{c[1]}</option>
                    ))}
                </select>
                Map tag value to HAWC tag
                <select onChange={e => store.setDatasetTagString(0, e.target.value)}>
                    {_.map(store.datasetTagChoices, c => (
                        <option value={c[0]}>{c[1]}</option>
                    ))}
                </select>
                <select onChange={e => store.setDatasetTagId(0, e.target.value)}>
                    {_.map(store.HAWCTagChoices, c => (
                        <option value={c[0]}>{c[1]}</option>
                    ))}
                </select>
                {JSON.stringify(store.datasetMap)}
            </div>
        );
    }
}

BulkTagReferencesMain.propTypes = {
    store: PropTypes.object,
};

export default BulkTagReferencesMain;
