import Endpoint from 'animal/Endpoint';
import Experiment from 'animal/Experiment';
import AnimalGroup from 'animal/AnimalGroup';
import Outcome from 'epi/Outcome';
import MetaResult from 'epimeta/MetaResult';
import IVEndpoint from 'invitro/IVEndpoint';
import IVChemical from 'invitro/IVChemical';
import Study from 'study/Study';

const modalClasses = {
    Endpoint,
    Experiment,
    AnimalGroup,
    Outcome,
    MetaResult,
    IVEndpoint,
    IVChemical,
    Study,
};

class GetModalClass {
    getClass(key) {
        return modalClasses[key];
    }
}

export default GetModalClass;
