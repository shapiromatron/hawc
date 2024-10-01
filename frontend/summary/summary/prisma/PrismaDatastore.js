import HAWCModal from "shared/utils/HAWCModal";
import h from "shared/utils/helpers";

class PrismaDatastore {
    constructor(settings, dataset) {
        this.settings = settings;
        this.dataset = dataset;
        this.settingsHash = h.hashString(JSON.stringify(this.settings));
        this.modal = new HAWCModal();
    }

    getDiagramSections() {
        const sections = this.settings.sections
            .filter(section => section.label.length > 0)
            .map(section => {
                return {
                    label: section.label,
                    key: section.key,
                    block_layout: "card",
                    blocks: [],
                };
            });
        return sections;
    }

    getConnections() {
        return [];
    }
}

export default PrismaDatastore;
