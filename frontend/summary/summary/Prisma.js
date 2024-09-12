import BaseVisual from "./BaseVisual";
import PrismaStore from "summary/summaryForms/stores/PrismaStore";

const startupPrismaAppRender = function (el, settings, datastore, options) {

    const store = new PrismaDataStore(settings, datastore, options);
    try {
        if (store.withinRenderableBounds) {
            store.initialize();
        }
        ReactDOM.render(
            <Provider store={store}>
                <PrismaComponent options={options} />
            </Provider>,
            el
        );
    } catch (err) {
        handleVisualError(err, $(el));
    }
};

@inject("store")
@observer
class PrismaComponent extends Component {
    componentDidMount() {
        const { store } = this.props,
            id = store.settingsHash,
            el = document.getElementById(id);

        if (el) {
            new PrismaPlot(store, this.props.options).render(el, tooltipEl);
        }
    }
    render() {
        const { store } = this.props,
            id = store.settingsHash,
            hasFilters = store.settings.filter_widgets.length > 0;

        if (!store.hasDataset) {
            return <Alert message={"No data are available."} />;
        }

        if (!store.withinRenderableBounds) {
            return <Alert message={`This Prisma visual is too large and cannot be rendered.`} />;
        }

        return (
            <>
                <div style={{ display: "flex", flexDirection: "row" }}>
                    <div style={{ flex: 9 }}>
                        <div id={id}>
                            <Loading />
                        </div>
                    </div>
                    <div id={`tooltip-${id}`} style={{ position: "absolute" }}></div>
                </div>
            </>
        );
    }
}
PrismaComponent.propTypes = {
    store: PropTypes.object,
    options: PropTypes.object.isRequired,
};


class Prisma extends BaseVisual {
    displayAsPage($el, options) {
        $el.html("Add Prisma diagram!");
    }

    displayAsModal(options) {}
}

export default Prisma;
