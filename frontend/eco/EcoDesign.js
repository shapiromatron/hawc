class EcoDesign {
    constructor(data) {
        this.data = data;
    }

    static get_detail_url(id) {
        return `/eco/design/${id}/`;
    }
}

export default EcoDesign;
