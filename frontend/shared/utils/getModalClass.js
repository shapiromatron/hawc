import AnimalGroup from "animal/AnimalGroup";
import Endpoint from "animal/Endpoint";
import Experiment from "animal/Experiment";
import Exposure from "epi/Exposure";
import Outcome from "epi/Outcome";
import StudyPopulation from "epi/StudyPopulation";
import MetaResult from "epimeta/MetaResult";
import IVChemical from "invitro/IVChemical";
import IVEndpoint from "invitro/IVEndpoint";
import Study from "study/Study";

const modalClasses = {
        Endpoint,
        Experiment,
        AnimalGroup,
        StudyPopulation,
        Exposure,
        Outcome,
        MetaResult,
        IVEndpoint,
        IVChemical,
        Study,
    },
    getModalClass = function (key) {
        return modalClasses[key];
    };

export default getModalClass;
