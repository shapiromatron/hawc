import Endpoint from "animal/Endpoint";
import Experiment from "animal/Experiment";
import AnimalGroup from "animal/AnimalGroup";
import StudyPopulation from "epi/StudyPopulation";
import Exposure from "epi/Exposure";
import Outcome from "epi/Outcome";
import MetaResult from "epimeta/MetaResult";
import IVEndpoint from "invitro/IVEndpoint";
import IVChemical from "invitro/IVChemical";
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
    getModalClass = function(key) {
        return modalClasses[key];
    };

export default getModalClass;
