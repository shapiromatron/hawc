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
        const {sections, boxes} = this.settings;
        return sections
            .filter(section => section.label.length > 0)
            .map(section => {
                return {
                    label: section.label,
                    key: section.key,
                    block_layout: "card",
                    blocks: boxes
                        .filter(b => b.section === section.key)
                        .map(b => {
                            return {
                                label: b.label,
                                key: b.key,
                                value: 123,
                            };
                        }),
                };
            });
    }

    getConnections() {
        return this.settings.arrows;
    }
}

export default PrismaDatastore;
