import _ from "lodash";
import DescriptiveTable from "shared/utils/DescriptiveTable";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";

import $ from "$";

class AnimalGroup {
    constructor(data) {
        this.data = data;
    }

    static get_detail_url(id) {
        return `/ani/animal-group/${id}/`;
    }

    static get_object(id, cb) {
        $.get(`/ani/api/animal-group/${id}/`, d => cb(new AnimalGroup(d)));
    }

    static displayAsModal(id) {
        AnimalGroup.get_object(id, d => d.displayAsModal());
    }

    build_breadcrumbs() {
        var urls = [
            {
                url: this.data.experiment.study.url,
                name: this.data.experiment.study.short_citation,
            },
            {
                url: this.data.experiment.url,
                name: this.data.experiment.name,
            },
            {
                url: this.data.url,
                name: this.data.name,
            },
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    }

    _getAniRelationLink(obj) {
        if (!obj) return undefined;
        return $(`<a href="${obj.url}">${obj.name}</a>`);
    }

    build_details_table() {
        var self = this,
            getRelations = function (lst) {
                return _.chain(lst)
                    .map(self._getAniRelationLink)
                    .map(d => $("<span>").append(d))
                    .value();
            },
            tbl;

        tbl = new DescriptiveTable()
            .add_tbody_tr("Name", this.data.name)
            .add_tbody_tr("Species", this.data.species)
            .add_tbody_tr("Strain", this.data.strain)
            .add_tbody_tr("Sex", this.data.sex)
            .add_tbody_tr("Source", this.data.animal_source)
            .add_tbody_tr("Lifestage exposed", this.data.lifestage_exposed)
            .add_tbody_tr("Lifestage assessed", this.data.lifestage_assessed)
            .add_tbody_tr("Generation", this.data.generation)
            .add_tbody_tr_list("Parents", getRelations(this.data.parents))
            .add_tbody_tr("Siblings", this._getAniRelationLink(this.data.siblings))
            .add_tbody_tr_list("Children", getRelations(this.data.children))
            .add_tbody_tr("Animal Husbandry", this.data.comments)
            .add_tbody_tr("Diet", this.data.diet);

        return tbl.get_tbl();
    }

    build_dr_details_table() {
        var self = this,
            data = this.data.dosing_regime,
            tbl,
            getExposureDuration = function (_d) {
                var txt = data.duration_exposure_text,
                    num = data.duration_exposure;

                if (txt && txt.length > 0) {
                    return txt;
                } else if (num && num >= 0) {
                    return `${num} days`;
                } else {
                    return undefined;
                }
            },
            getDurationObservation = function (_d) {
                var duration_observation = data.duration_observation;
                return duration_observation ? `${duration_observation} days` : undefined;
            },
            getDoses = function (doses) {
                if (doses.length === 0) {
                    return undefined;
                }

                let grps = _.chain(doses)
                    .sortBy(d => d.dose_group_id)
                    .groupBy(d => d.dose_units.name)
                    .value();

                return _.map(grps, (groups, units) => {
                    let ds = _.map(groups, d => d.dose.toString()).join(", ");
                    return `${ds} ${units}`;
                });
            },
            getDosedAnimals = function (id_, dosed_animals) {
                // only show dosed-animals if dosing-regime not applied to these animals
                var ag = id_ !== dosed_animals.id ? dosed_animals : undefined;
                return self._getAniRelationLink(ag);
            };

        tbl = new DescriptiveTable()
            .add_tbody_tr("Dosed animals", getDosedAnimals(this.data.id, data.dosed_animals))
            .add_tbody_tr("Route of exposure", data.route_of_exposure)
            .add_tbody_tr("Exposure duration", getExposureDuration())
            .add_tbody_tr("Duration observation", getDurationObservation())
            .add_tbody_tr("Number of dose-groups", data.num_dose_groups)
            .add_tbody_tr("Positive control", data.positive_control)
            .add_tbody_tr("Negative control", data.negative_control)
            .add_tbody_tr_list("Doses", getDoses(data.doses))
            .add_tbody_tr("Description", data.description);

        return tbl.get_tbl();
    }

    displayAsModal() {
        var modal = new HAWCModal(),
            title = $("<h4>").html(this.build_breadcrumbs()),
            $details = $('<div class="col-md-12">'),
            $content = $('<div class="container-fluid">').append(
                $('<div class="row">').append($details)
            );

        this.render($details);

        modal.addHeader(title).addBody($content).addFooter("").show({maxWidth: 1000});
    }

    render($div) {
        $div.append(
            this.build_details_table(),
            $("<h3>Dosing regime</h3>"),
            this.build_dr_details_table()
        );
    }
}

export default AnimalGroup;
