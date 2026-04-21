import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import HelpTextPopup from "shared/components/HelpTextPopup";
import Modal from "shared/components/Modal";
import WaitLoad from "shared/components/WaitLoad";

import {seErrorWarning, testFootnotes} from "../constants";
import {ff, fractionalFormatter, parameterFormatter} from "../formatters";
import DoseResponsePlot from "./DoseResponsePlot";
import Table from "./Table";

const showDegree = model => {
        const name = model.name.toLowerCase();
        return name.includes("polynomial") || name.includes("multistage");
    },
    getParamPriors = function (model) {
        const {parameters} = model.results;
        return _.range(parameters.names.length).map(i => {
            return [
                parameters.names[i],
                ff(parameters.prior_initial_value[i]),
                ff(parameters.prior_min_value[i]),
                ff(parameters.prior_max_value[i]),
            ];
        });
    },
    getParamFooter = function (model) {
        const bounded = _.sum(model.results.parameters.bounded) > 0;
        return bounded ? <p className="text-sm">{seErrorWarning}</p> : null;
    },
    getParams = function (model) {
        const {parameters} = model.results;
        return _.range(parameters.names.length).map(i => {
            return [
                parameters.names[i],
                parameters.bounded[i] ? (
                    <span key={0}>
                        On Bound
                        <HelpTextPopup
                            title={"On Bound"}
                            content={`The value of this parameter, ${parameters.values[i]}, is within the tolerance of the bound`}
                        />
                    </span>
                ) : (
                    parameterFormatter(parameters.values[i])
                ),
                parameters.bounded[i] ? (
                    <span key={i} title={parameters.se[i]}>
                        Not Reported
                    </span>
                ) : (
                    parameterFormatter(parameters.se[i])
                ),
            ];
        });
    };

@inject("store")
@observer
class ModelModal extends React.Component {
    renderContinuousBody() {
        const {store} = this.props,
            model = store.modalModel,
            {results} = model,
            getGofData = function () {
                const {gof} = model.results;
                return _.range(gof.dose.length).map(i => {
                    return [
                        gof.dose[i],
                        gof.size[i],
                        gof.obs_mean[i],
                        ff(gof.est_mean[i]),
                        gof.obs_sd[i],
                        ff(gof.est_sd[i]),
                        ff(gof.residual[i]),
                    ];
                });
            },
            getLikelihoodData = function () {
                const {deviance} = model.results;
                return _.range(deviance.names.length).map(i => {
                    return [
                        deviance.names[i],
                        ff(deviance.loglikelihoods[i]),
                        deviance.num_params[i],
                        ff(deviance.aics[i]),
                    ];
                });
            },
            getTestData = function () {
                const {tests} = model.results;
                return _.range(tests.names.length).map(i => {
                    return [
                        <span key={0}>
                            Test {i + 1}
                            <HelpTextPopup title={`Test ${i + 1}`} content={testFootnotes[i + 1]} />
                        </span>,
                        ff(tests.ll_ratios[i]),
                        ff(tests.dfs[i]),
                        fractionalFormatter(tests.p_values[i]),
                    ];
                });
            };
        return (
            <div className="row">
                <div className="col-lg-6">
                    <Table
                        label="Model Options"
                        extraClasses="col-r-2"
                        colWidths={[60, 40]}
                        data={_.compact([
                            ["BMR Type", store.bmrTypeLabel],
                            ["BMRF", ff(model.settings.bmr)],
                            ["Distribution Type", store.distributionType],
                            ["Confidence Level (one sided)", 1 - ff(model.settings.alpha)],
                            showDegree(model) ? ["Degree", model.settings.degree] : undefined,
                        ])}
                    />
                </div>
                <div className="col-lg-5">
                    <Table
                        label="Parameter Settings"
                        extraClasses="text-right col-l-1"
                        colWidths={[25, 25, 25, 25]}
                        colNames={["Name", "Initial Value", "Min Value", "MaxValue"]}
                        data={getParamPriors(model)}
                    />
                </div>
                <div className="col-lg-4">
                    <Table
                        label="Modeling Summary"
                        extraClasses="col-r-2"
                        colWidths={[60, 40]}
                        data={[
                            ["BMD", ff(results.bmd)],
                            ["BMDL", ff(results.bmdl)],
                            ["BMDU", ff(results.bmdu)],
                            ["AIC", ff(results.fit.aic)],
                            ["P-Value", fractionalFormatter(results.tests.p_values[3])],
                            ["Model d.f.", results.tests.dfs[3]],
                            ["Log-Likelihood", ff(results.fit.loglikelihood)],
                        ]}
                    />
                </div>
                <div className="col-lg-8" style={{height: 400}}>
                    <WaitLoad>
                        <DoseResponsePlot showDataset={true} showSelected={true} showModal={true} />
                    </WaitLoad>
                </div>
                <div className="col-xl-7">
                    <Table
                        label="Model Parameters"
                        extraClasses="text-right col-l-1"
                        colWidths={[33, 33, 33]}
                        colNames={["Variable", "Estimate", "Standard Error"]}
                        data={getParams(model)}
                        footer={getParamFooter(model)}
                    />
                </div>
                <div className="col-xl-12">
                    <Table
                        label="Goodness of Fit"
                        extraClasses="text-right"
                        colWidths={[14, 14, 14, 14, 14, 14, 14]}
                        colNames={[
                            "Dose",
                            "N",
                            "Sample Mean",
                            "Model Fitted Mean",
                            "Sample SD",
                            "Model Fitted SD",
                            "Scaled Residual",
                        ]}
                        data={getGofData()}
                    />
                </div>
                <div className="col-xl-8">
                    <Table
                        label="Likelihoods"
                        extraClasses="text-right col-l-1"
                        colWidths={[25, 25, 25, 25]}
                        colNames={["Model", "Log-Likelihood", "N Parameters", "AIC"]}
                        data={getLikelihoodData()}
                    />
                </div>
                <div className="col-xl-8">
                    <Table
                        label="Tests of Mean and Variance Fits"
                        extraClasses="text-right col-l-1"
                        colWidths={[25, 25, 25, 25]}
                        colNames={["Test", "-2 * Log(Likelihood Ratio)", "Test d.f.", "P-Value"]}
                        data={getTestData()}
                    />
                </div>
            </div>
        );
    }
    renderDichotomousBody() {
        const {store} = this.props,
            model = store.modalModel,
            {results} = model,
            getGofData = function () {
                const {gof} = model.results,
                    {dataset} = store;
                return _.range(gof.residual.length).map(i => {
                    return [
                        dataset.doses[i],
                        dataset.ns[i],
                        dataset.incidences[i],
                        ff(gof.expected[i]),
                        ff(gof.expected[i] / dataset.ns[i]),
                        ff(gof.residual[i]),
                    ];
                });
            },
            getLikelihoodData = function () {
                const {deviance} = model.results;
                return _.range(deviance.names.length).map(i => {
                    return [
                        deviance.names[i],
                        ff(deviance.ll[i]),
                        deviance.params[i],
                        i === 0 ? "-" : ff(deviance.deviance[i]),
                        i === 0 ? "-" : deviance.df[i],
                        i === 0 ? "-" : fractionalFormatter(deviance.p_value[i]),
                    ];
                });
            };
        return (
            <div className="row">
                <div className="col-lg-6">
                    <Table
                        label="Model Options"
                        extraClasses="col-r-2"
                        colWidths={[60, 40]}
                        data={_.compact([
                            ["BMR Type", store.bmrTypeLabel],
                            ["BMR", ff(model.settings.bmr)],
                            ["Confidence Level (one sided)", 1 - ff(model.settings.alpha)],
                            showDegree(model) ? ["Degree", model.settings.degree] : undefined,
                        ])}
                    />
                </div>
                <div className="col-lg-6">
                    <Table
                        label="Parameter Settings"
                        extraClasses="text-right col-l-1"
                        colWidths={[25, 25, 25, 25]}
                        colNames={["Name", "Initial Value", "Min Value", "MaxValue"]}
                        data={getParamPriors(model)}
                    />
                </div>
                <div className="col-lg-4">
                    <Table
                        label="Modeling Summary"
                        extraClasses="col-r-2"
                        colWidths={[60, 40]}
                        data={[
                            ["BMD", ff(results.bmd)],
                            ["BMDL", ff(results.bmdl)],
                            ["BMDU", ff(results.bmdu)],
                            ["AIC", ff(results.fit.aic)],
                            ["P-Value", fractionalFormatter(results.gof.p_value)],
                            ["Model d.f.", results.gof.df],
                            ["Log-Likelihood", ff(results.fit.loglikelihood)],
                            ["Chi²", ff(results.chi_squared)],
                        ]}
                    />
                </div>
                <div className="col-lg-8" style={{height: 400}}>
                    <WaitLoad>
                        <DoseResponsePlot showDataset={true} showSelected={true} showModal={true} />
                    </WaitLoad>
                </div>
                <div className="col-xl-8">
                    <Table
                        label="Model Parameters"
                        extraClasses="text-right col-l-1"
                        colWidths={[33, 33, 33]}
                        colNames={["Variable", "Estimate", "Standard Error"]}
                        data={getParams(model)}
                        footer={getParamFooter(model)}
                    />
                </div>
                <div className="col-xl-8">
                    <Table
                        label="Goodness of Fit"
                        extraClasses="text-right"
                        colWidths={[20, 15, 15, 15, 15, 15]}
                        colNames={[
                            "Dose",
                            "N",
                            "Observed",
                            "Expected",
                            "Estimated Probability",
                            "Scaled Residual",
                        ]}
                        data={getGofData()}
                    />
                </div>
                <div className="col-xl-8">
                    <Table
                        label="Analysis of Deviance"
                        extraClasses="text-right col-l-1"
                        colWidths={[20, 15, 15, 15, 15, 15]}
                        colNames={[
                            "Model",
                            "Log-Likelihood",
                            "N Parameters",
                            "Deviance",
                            "Test d.f.",
                            "P-Value",
                        ]}
                        data={getLikelihoodData()}
                    />
                </div>
            </div>
        );
    }
    render() {
        const {store} = this.props,
            {showModal, hideModal, modalModel} = store;
        if (!showModal) {
            return null;
        }
        return (
            <Modal isShown={showModal} onClosed={hideModal}>
                <div className="modal-header pb-0">
                    <h4>{modalModel.name}</h4>
                    <button
                        type="button"
                        className="float-right close"
                        data-dismiss="modal"
                        onClick={hideModal}
                        aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div className="modal-body">
                    {store.isContinuous ? this.renderContinuousBody() : null}
                    {store.isDichotomous ? this.renderDichotomousBody() : null}
                </div>
            </Modal>
        );
    }
}
ModelModal.propTypes = {
    store: PropTypes.object,
};

export default ModelModal;
