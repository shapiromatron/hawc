import AnimalGroup from "animal/AnimalGroup";
import Endpoint from "animal/Endpoint";
import Experiment from "animal/Experiment";
import EcoDesign from "eco/EcoDesign";
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
Configuration requirements:
---------------------------
key: must be unique item for action
columns: valid column names for this action
cls: class for rendering; must implement a `get_detail_url` and `displayAsModal`
label: label for displaying action for users configuring interactivity
modal: display modal on click
*/

export default [
    // lit
    {
        key: "reference",
        columns: ["reference id"],
        cls: Reference,
        label: "Show reference",
        modal: false,
    },
    {
        key: "hero",
        columns: ["hero id", "HERO ID", "hero_id"],
        cls: Reference,
        label: "Show HERO",
        modal: false,
    },
    {
        key: "pubmed",
        columns: ["pubmed id", "PMID", "pubmed_id"],
        cls: Reference,
        label: "Show PubMed",
        modal: false,
    },
    // study
    {
        key: "study",
        columns: ["study id", "study_id", "study-id"],
        cls: Study,
        label: "Show study",
        modal: true,
    },
    // animal
    {
        key: "experiment",
        columns: ["experiment id"],
        cls: Experiment,
        label: "Show animal experiment",
        modal: true,
    },
    {
        key: "animal_group",
        columns: ["animal group id"],
        cls: AnimalGroup,
        label: "Show animal group",
        modal: true,
    },
    {
        key: "endpoint",
        columns: ["endpoint id"],
        cls: Endpoint,
        label: "Show animal endpoint (basic)",
        modal: true,
    },
    // TODO - migrate data; remove old endpoint_complete and migrate behavior to endpoint
    {
        key: "endpoint_complete",
        columns: ["endpoint id"],
        cls: Endpoint,
        label: "Show animal endpoint (complete)",
        modal: true,
    },
    //eco
    {
        key: "eco_design",
        columns: ["design-id"],
        cls: EcoDesign,
        label: "Show ecology design",
        modal: false,
    },
    // epi
    {
        key: "study_population",
        columns: ["study population id"],
        cls: StudyPopulation,
        label: "Show epi study population",
        modal: true,
    },
    {
        key: "comparison_set",
        columns: ["comparison set id"],
        cls: ComparisonSet,
        label: "Show epi comparison set",
        modal: true,
    },
    {
        key: "exposure",
        columns: ["exposure id"],
        cls: Exposure,
        label: "Show epi exposure",
        modal: true,
    },
    {key: "outcome", columns: ["outcome id"], cls: Outcome, label: "Show epi outcome", modal: true},
    {key: "result", columns: ["result id"], cls: Result, label: "Show epi result", modal: true},
    // epimeta
    {
        key: "meta_protocol",
        columns: ["protocol id"],
        cls: MetaProtocol,
        label: "Show epi meta protocol",
        modal: true,
    },
    {
        key: "meta_result",
        columns: ["meta result id"],
        cls: MetaResult,
        label: "Show epi meta result",
        modal: true,
    },
    // invitro
    {
        key: "iv_chemical",
        columns: ["chemical id"],
        cls: IVChemical,
        label: "Show invitro chemical",
        modal: true,
    },
    {
        key: "iv_experiment",
        columns: ["IVExperiment id"],
        cls: IVExperiment,
        label: "Show invitro experiment",
        modal: true,
    },
    {
        key: "iv_celltype",
        columns: ["IVCellType id"],
        cls: IVCellType,
        label: "Show invitro cell type",
        modal: true,
    },
    {
        key: "iv_endpoint",
        columns: ["IVEndpoint id"],
        cls: IVEndpoint,
        label: "Show invitro endpoint",
        modal: true,
    },
];
