import _ from "lodash";
import Prisma from "summary/summary/Prisma";

import BaseVisualForm from "./BaseVisualForm";
import {TextField} from "./Fields";

class PrismaForm extends BaseVisualForm {
    buildPreview($parent, data) {
        this.preview = new Prisma(data).displayAsPage($parent.empty(), {dev: true});
    }

    initDataForm() {}

    updateSettingsFromPreview() {}
}

_.extend(PrismaForm, {
    tabs: [{name: "overall", label: "Main tab"}],
    schema: [{type: TextField, name: "title", label: "Title", def: "Title", tab: "overall"}],
});

export default PrismaForm;
