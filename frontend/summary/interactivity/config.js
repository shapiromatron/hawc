import AnimalGroup from "animal/AnimalGroup";
import Endpoint from "animal/Endpoint";
import Experiment from "animal/Experiment";
import ComparisonSet from "epi/ComparisonSet";
import Exposure from "epi/Exposure";
import Outcome from "epi/Outcome";
import Result from "epi/Result";
import StudyPopulation from "epi/StudyPopulation";
import MetaProtocol from "epimeta/MetaProtocol";
import MetaResult from "epimeta/MetaResult";
import IVCellType from "invitro/IVCellType";
import IVChemical from "invitro/IVChemical";
import IVEndpoint from "invitro/IVEndpoint";
import IVExperiment from "invitro/IVExperiment";
import Reference from "lit/Reference";
import Study from "study/Study";

/*
key: unique item for action
columns: column names
cls: label to render
label: label for interactivity dropdown configuration
modal: display modal on click
*/

export default {
    // lit
    reference: {columns: ["reference id"], cls: Reference, label: "Show reference", modal: false},
    hero: {columns: ["hero id"], cls: Reference, label: "Show HERO", modal: false},
    pubmed: {columns: ["pubmed id"], cls: Reference, label: "Show PubMed", modal: false},
    // study
    study: {columns: ["study id"], cls: Study, label: "Show study", modal: true},
    // animal
    experiment: {
        columns: ["experiment id"],
        cls: Experiment,
        label: "Show animal experiment",
        modal: true,
    },
    animal_group: {
        columns: ["animal group id"],
        cls: AnimalGroup,
        label: "Show animal group",
        modal: true,
    },
    endpoint: {
        columns: ["endpoint id"],
        cls: Endpoint,
        label: "Show animal endpoint (basic)",
        modal: true,
    },
    // TODO - migrate data; remove old endpoint_complete and migrate behavior to endpoint
    endpoint_complete: {
        columns: ["endpoint id"],
        cls: Endpoint,
        label: "Show animal endpoint (complete)",
        modal: true,
    },
    // epi
    study_population: {
        columns: ["study population id"],
        cls: StudyPopulation,
        label: "Show epi study population",
        modal: true,
    },
    comparison_set: {
        columns: ["comparison set id"],
        cls: ComparisonSet,
        label: "Show epi comparison set",
        modal: true,
    },
    exposure: {columns: ["exposure id"], cls: Exposure, label: "Show epi exposure", modal: true},
    outcome: {columns: ["outcome id"], cls: Outcome, label: "Show epi outcome", modal: true},
    result: {columns: ["result id"], cls: Result, label: "Show epi result", modal: true},
    // epimeta
    meta_protocol: {
        columns: ["protocol id"],
        cls: MetaProtocol,
        label: "Show epi meta protocol",
        modal: true,
    },
    meta_result: {
        columns: ["meta result id"],
        cls: MetaResult,
        label: "Show epi meta result",
        modal: true,
    },
    // invitro
    iv_chemical: {
        columns: ["chemical id"],
        cls: IVChemical,
        label: "Show invitro chemical",
        modal: true,
    },
    iv_experiment: {
        columns: ["IVExperiment id"],
        cls: IVExperiment,
        label: "Show invitro experiment",
        modal: true,
    },
    iv_celltype: {
        columns: ["IVCellType id"],
        cls: IVCellType,
        label: "Show invitro cell type",
        modal: true,
    },
    iv_endpoint: {
        columns: ["IVEndpoint id"],
        cls: IVEndpoint,
        label: "Show invitro endpoint",
        modal: true,
    },
};
