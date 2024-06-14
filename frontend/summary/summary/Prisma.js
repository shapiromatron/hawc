import BaseVisual from "./BaseVisual";

class Prisma extends BaseVisual {
    displayAsPage($el, options) {
        $el.html("Add Prisma diagram!");
    }

    displayAsModal(options) {}
}

export default Prisma;
