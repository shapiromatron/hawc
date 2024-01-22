import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Loading from "shared/components/Loading";

import EditContainer from "./EditContainer";

const getHeaderByTitle = function (item) {
    switch (item.depth) {
        case 2:
            return <h2 id={item.slug}>{item.title}</h2>;
        case 3:
            return <h3 id={item.slug}>{item.title}</h3>;
        case 4:
            return <h4 id={item.slug}>{item.title}</h4>;
        case 5:
            return <h5 id={item.slug}>{item.title}</h5>;
        case 6:
        default:
            return <h6 id={item.slug}>{item.title}</h6>;
    }
};

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        const {store} = this.props;
        store.fetchItems();
    }

    componentDidUpdate() {
        const {store} = this.props;
        store.renderSmartTags();
    }

    render() {
        const {store} = this.props,
            {editMode} = store.config;
        if (!store.hasItems) {
            return <Loading />;
        }
        return (
            <div className="row">
                <div className="col-md-9">
                    {editMode ? (
                        <EditContainer />
                    ) : (
                        store.visibleItems.map(item => (
                            <div key={item.id}>
                                {getHeaderByTitle(item)}
                                <div dangerouslySetInnerHTML={{__html: item.text}}></div>
                            </div>
                        ))
                    )}
                    {!editMode && store.visibleItems.length === 0 ? (
                        <p>
                            <i>No summary text exists for this assessment.</i>
                        </p>
                    ) : null}
                </div>
                <div
                    id="st-sidebar"
                    className="col-md-3 py-3"
                    style={{
                        backgroundColor: "#e9ecef",
                        borderLeft: "3px solid grey",
                    }}>
                    {editMode ? (
                        <button
                            className="btn btn-primary float-right"
                            onClick={() => store.createItem()}>
                            <i className="fa fa-fw fa-plus"></i>&nbsp;New
                        </button>
                    ) : null}
                    <h4 className="py-2">Document structure</h4>
                    <hr />
                    <nav id="st-headers-nav" className="nav flex-column nav-pills">
                        {editMode
                            ? store.visibleItems.map(item => (
                                  <a
                                      key={item.id}
                                      style={{paddingLeft: 15 * (item.depth - 2)}}
                                      href="#"
                                      className="nav-link"
                                      onClick={e => {
                                          e.preventDefault();
                                          store.updateItem(item);
                                      }}>
                                      {item.title}
                                  </a>
                              ))
                            : store.visibleItems.map(item => (
                                  <a
                                      key={item.id}
                                      style={{paddingLeft: 15 * (item.depth - 2)}}
                                      className="nav-link"
                                      href={`#${item.slug}`}>
                                      {item.title}
                                  </a>
                              ))}
                    </nav>
                </div>
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
