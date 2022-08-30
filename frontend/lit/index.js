import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import Reference from "./Reference";
import ReferenceComponent from "./components/Reference";
import ReferenceSearchMain from "./ReferenceSearch/Main";
import ReferenceSearchStore from "./ReferenceSearch/store";
import ReferenceTreeMain from "./ReferenceTreeBrowse/Main";
import ReferenceTreeMainStore from "./ReferenceTreeBrowse/store";
import TagReferencesMain from "./TagReferences/Main";
import TagReferencesMainStore from "./TagReferences/store";
import BulkTagReferencesMain from "./BulkTagReferences/Main";
import BulkTagReferencesMainStore from "./BulkTagReferences/store";
import TagTree from "./TagTree";
import TagTreeViz from "./TagTreeViz";
import TagConflictsMain from "./TagConflicts/Main";
import TagConflictsMainStore from "./TagConflicts/store";

export default {
    TagTree,
    startupReferenceDetail(el, config) {
        let tagtree = new TagTree(config.tags[0]),
            ref = new Reference(config.reference, tagtree),
            options = {
                showActions: config.canEdit,
                actionsBtnClassName: "btn-primary",
            };

        ReactDOM.render(<ReferenceComponent reference={ref} {...options} />, el);
    },
    startupSearchReference(el, config) {
        ReactDOM.render(
            <Provider store={new ReferenceSearchStore(config)}>
                <ReferenceSearchMain />
            </Provider>,
            el
        );
    },
    startupReferenceList(el, config) {
        ReactDOM.render(
            <Provider store={new ReferenceTreeMainStore(config)}>
                <ReferenceTreeMain />
            </Provider>,
            el
        );
    },
    startupTagReferences(el, config) {
        ReactDOM.render(
            <Provider store={new TagReferencesMainStore(config)}>
                <TagReferencesMain />
            </Provider>,
            el
        );
    },
    startupBulkTagReferences(el, config) {
        ReactDOM.render(
            <Provider store={new BulkTagReferencesMainStore(config)}>
                <BulkTagReferencesMain />
            </Provider>,
            el
        );
    },
    startupTagTreeViz(el, config) {
        let tagtree = new TagTree(config.tags[0], config.assessment_id, config.search_id),
            settings = {
                hide_empty_tag_nodes: false,
                width: 1280,
                height: 800,
                can_edit: config.can_edit,
                show_legend: true,
                show_counts: true,
            };
        tagtree.rename_top_level_node(config.assessment_name);
        tagtree.add_references(config.references);
        new TagTreeViz(tagtree, el, config.title, settings);
    },
    startupConflict(el, config) {
        ReactDOM.render(
            <Provider store={new TagConflictsMainStore(config)}>
                <TagConflictsMain />
            </Provider>,
            el
        );
    },
};
