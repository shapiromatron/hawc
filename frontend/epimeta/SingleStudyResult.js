class SingleStudyResult {
    constructor(data) {
        this.data = data;
    }

    build_table_row() {
        return [
            this.study_link(),
            this.data.weight || "-",
            this.data.n || "-",
            this.data.estimateFormatted || "-",
            this.data.notes || "-",
        ];
    }

    study_link() {
        var txt = this.data.exposure_name;

        if (this.data.study) {
            txt =
                '<a href="{0}">{1}</a>: '.printf(
                    this.data.study.url,
                    this.data.study.short_citation
                ) + txt;
        }

        return txt;
    }
}

export default SingleStudyResult;
