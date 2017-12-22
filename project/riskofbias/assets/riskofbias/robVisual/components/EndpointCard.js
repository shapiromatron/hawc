import React, { Component } from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';

import CardHeader from './CardHeader';
import DoseResponseChart from './Graph/DoseResponseChart';
import Content from './Content';
import Endpoint from 'animal/Endpoint';
import Study from 'study/Study';
import './EndpointCard.css';

class EndpointCard extends Component {
    constructor(props) {
        super(props);
        this.showEndpointModal = this.showEndpointModal.bind(this);
        this.showStudyModal = this.showStudyModal.bind(this);
    }

    groupByDoseUnit() {
        let doses = this.props.endpoint.animal_group.dosing_regime.doses;
        return _.chain(doses)
            .map((dose) => {
                return {
                    unit: dose.dose_units.name,
                    dose: dose.dose,
                    id: dose.dose_group_id,
                };
            })
            .groupBy('unit')
            .toArray()
            .value();
    }

    filterNullData() {
        let { endpoint } = this.props,
            responses = _.filter(
                _.map(endpoint.groups, (group) => {
                    return {
                        response: group.response,
                        significant: group.significant,
                        unit: endpoint.response_units,
                        id: group.dose_group_id,
                    };
                }),
                (response) => {
                    return response.response !== null;
                }
            ),
            ids = _.map(responses, 'id'),
            doses = _.map(this.groupByDoseUnit(), (doseGroup) => {
                return _.filter(doseGroup, (dose) => {
                    return _.includes(ids, dose.id);
                });
            });
        return { doses, responses };
    }

    showStudyModal(e) {
        Study.displayAsModal(e.target.id);
    }

    showEndpointModal(e) {
        Endpoint.displayAsModal(e.target.id);
    }

    getChartData() {
        let height = 150,
            width = 300,
            radius = 130,
            padding = [20, 0, 50, 55],
            yTransform = [padding[3], 0],
            xTransform = [0, height - padding[2]];
        return { height, width, padding, yTransform, xTransform, radius };
    }

    renderNullData() {
        return <h4 className="nullNotification">Endpoint contains empty data.</h4>;
    }

    renderChart(doses, responses) {
        let { endpoint } = this.props,
            chartData = this.getChartData();
        return (
            <DoseResponseChart
                className="doseResponseChart"
                endpoint={endpoint}
                doses={doses[0]}
                responses={responses}
                chartData={chartData}
            />
        );
    }

    render() {
        let { endpoint, study } = this.props,
            { doses, responses } = this.filterNullData(),
            dataNull = _.isEmpty(doses) || _.isEmpty(responses),
            content_types = ['results_notes', 'system', 'organ', 'effect', 'effect_subtype'];
        return (
            <div className="endpointCard">
                <CardHeader
                    endpoint={endpoint}
                    study={study}
                    citation={endpoint.animal_group.experiment.study.short_citation}
                    showEndpointModal={this.showEndpointModal}
                    showStudyModal={this.showStudyModal}
                />
                {dataNull ? this.renderNullData() : this.renderChart(doses, responses)}
                <Content data={endpoint} content_types={content_types} />
            </div>
        );
    }
}

EndpointCard.propTypes = {
    endpoint: PropTypes.object.isRequired,
};

export default EndpointCard;
