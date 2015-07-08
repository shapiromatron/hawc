from django.utils.html import strip_tags

from docxUtils.tables import TableMaker

from utils.helper import HAWCDOCXReport

from animal import models


class EndpointDOCXReport(HAWCDOCXReport):

    @staticmethod
    def getDoses(ag):
        # dictionary-mapping where keys are dose-units and doses are list of floats
        doses = {}
        for d in ag['dosing_regime']['doses']:
            units = d['dose_units']['units']
            if units not in doses:
                doses[units] = []
            doses[units].append(d['dose'])
        return doses

    @staticmethod
    def getDoseText(doses):
        dose_txt = []
        for unit in doses.keys():
            dose_txt.append(u"{0} {1}".format(u", ".join([
                unicode(dose) for dose in doses[unit]]), unit))
        return u"\n".join(dose_txt)

    @staticmethod
    def getPurityText(exp):
        txt = u"NR"
        if exp["purity_available"]:
            txt = u">{0}%".format(exp["purity"])
            if exp["chemical_source"]:
                txt += u" {}".format(exp["chemical_source"])
        return txt

    @staticmethod
    def getStrainSource(ag):
        return u"{} {}".format(ag["strain"], ag["animal_source"])

    @staticmethod
    def getCOItext(study):
        txt = study["coi_reported"]
        if study["coi_details"] != "":
            txt = u"{} ({})".format(txt, study["coi_details"])
        return txt

    @staticmethod
    def getAdditionalEndpoints(eps):
        return u", ".join(ep["name"] for ep in eps if ep["data_extracted"] is False)

    @staticmethod
    def getEndpointsText(eps):
        return u", ".join(ep["name"] for ep in eps if ep["data_extracted"] is True)

    @staticmethod
    def getNText(eps):
        ns = []
        for ep in eps:
            ns.extend([eg["n"] for eg in ep["endpoint_group"]])
        return models.EndpointGroup.getNRangeText(ns)

    @staticmethod
    def getStatisticalAnalysis(eps):
        return u"; ".join(set([ep["statistical_test"] for ep in eps]))

    @staticmethod
    def getStatisticalPowers(eps):
        return u"; ".join(set([ep["power_notes"] for ep in eps]))

    @staticmethod
    def printField(runs, heading, text):
        """
        Create a field-level run. The heading is bolded, the text is not-bolded.
        They will appear with no newline character between the two.
        """
        runs.append(TableMaker.new_run(heading, b=True, newline=False))
        runs.append(TableMaker.new_run(text))

    def getStudyDetailsRuns(self, ag, doses):

        runs = []

        txt = "({})".format(ag['experiment']['study']['short_citation'])
        runs.append(TableMaker.new_run(txt, b=True))

        self.printField(
            runs, "Species: ", ag["species"])
        self.printField(
            runs, "Strain (source): ", self.getStrainSource(ag))
        self.printField(
            runs, "Sex: ", ag["sex"])
        self.printField(
            runs, "Doses: ", self.getDoseText(doses))
        self.printField(
            runs, "Purity (source): ", self.getPurityText(ag["experiment"]))
        self.printField(
            runs, "Dosing period: ", strip_tags(ag["dosing_regime"]["description"]))
        self.printField(
            runs, "Route: ", ag["dosing_regime"]["route_of_exposure"])
        self.printField(
            runs, "Diet: ", ag["experiment"]["diet"])
        self.printField(
            runs, "Negative controls: ", ag["dosing_regime"]["negative_control"])
        self.printField(
            runs, "Funding source: ", ag["experiment"]["study"]["funding_source"])
        self.printField(
            runs, "Author conflict of interest: ", self.getCOItext(ag["experiment"]["study"]))
        self.printField(
            runs, "Comments: ", strip_tags(ag["experiment"]["description"]))

        return runs

    def getHealthOutcomes(self, ag):
        runs = []
        self.printField(
            runs, "Endpoints: ", self.getEndpointsText(ag["eps"]))
        self.printField(
            runs, "Age at exposure: ", ag["lifestage_exposed"])
        self.printField(
            runs, "Age at assessment: ", ag["lifestage_assessed"])
        self.printField(
            runs, "N: ", self.getNText(ag["eps"]))
        self.printField(
            runs, "Statistical analysis: ", self.getStatisticalAnalysis(ag["eps"]))
        self.printField(
            runs, "Control for litter effects: ", ag["experiment"]["litter_effects"])
        self.printField(
            runs, "Statistical power: ", self.getStatisticalPowers(ag["eps"]))
        self.printField(
            runs, "Additional endpoints not extracted: ", self.getAdditionalEndpoints(ag["eps"]))

        return runs

    def build_summary_table(self, ag):
        widths = [2.5, 2.7, 1.5, 0.5, 1.2, 1.6]
        tbl = TableMaker(widths, numHeaders=3, firstRowCaption=True, tblStyle="ntpTbl")

        doses = self.getDoses(ag)
        firstDose = doses.keys()[0]

        # add caption
        tbl.new_td_txt(0, 0, ag['name'], colspan=6)

        # add headers
        tbl.new_th(1, 0, r'Reference, Animal Model, and Dosing', rowspan=2)
        tbl.new_th(1, 1, r'Health outcome', rowspan=2)
        tbl.new_th(1, 2, r'Results', colspan=4)

        tbl.new_th(2, 2, u'Dose ({0})'.format(firstDose))
        tbl.new_th(2, 3, r'N')
        tbl.new_th(2, 4, u'Mean \u00B1 SD',)
        tbl.new_th(2, 5, r'% control (95% CI)')

        # build endpoint rows
        rows = 3
        for ep in ag["eps"]:

            if ep["data_extracted"] == False:
                continue

            # add endpoint-name as first-row
            tbl.new_td_run(
                rows, 2,
                [TableMaker.new_run(ep["name"], i=True, newline=False)],
                colspan=4
            )
            rows += 1

            # build column-header table
            data_type = ep["data_type"]
            for i, eg in enumerate(ep["endpoint_group"]):

                ci = []
                resp = u"-"

                if data_type == "C":
                    resp = unicode(eg.get("response", "-"))
                    if eg.get('stdev') is not None:
                        resp += u' \u00B1 {0:.2f}'.format(eg["stdev"])
                elif data_type in ["D", "DC"]:
                    if eg.get("incidence") is not None:
                        resp = u'{0}/{1}'.format(eg["incidence"], eg["n"])
                    ci.append(u"NR")
                else:  # ["P"]
                    resp = u'NR'

                if i != 0 and eg.get("percentControlMean") is not None:
                    ci.append("{0:.1f}".format(eg["percentControlMean"]))
                if eg.get("percentControlLow") is not None and eg.get("percentControlHigh") is not None:
                    ci.append(u'({0:.1f}, {1:.1f})'.format(eg["percentControlLow"], eg["percentControlHigh"]))
                ci = u" ".join(ci)

                tbl.new_td_txt(rows, 2, unicode(doses[firstDose][i]))
                tbl.new_td_txt(rows, 3, unicode(eg.get("n", "-")))
                tbl.new_td_txt(rows, 4, resp)
                tbl.new_td_txt(rows, 5, ci)
                rows += 1
        else:
            # add blank cells if none-exist
            tbl.new_td_txt(3, 2, "")
            tbl.new_td_txt(3, 3, "")
            tbl.new_td_txt(3, 4, "")
            tbl.new_td_txt(3, 5, "")

        # adjust rowspans for summary rows
        rowspan = rows - 3
        tbl.new_td_run(3, 0, self.getStudyDetailsRuns(ag, doses), rowspan=rowspan)
        tbl.new_td_run(3, 1, self.getHealthOutcomes(ag), rowspan=rowspan)

        tbl.render(self.doc)
        self.doc.add_paragraph("\n")

    def create_content(self):
        d = self.context

        self.setLandscape()
        self.setMargins(left=0.5, right=0.5)

        # title
        txt = "Bioassay report: {0}".format(d['assessment']['name'])
        self.doc.add_heading(txt, 1)

        # loop through each study
        for study in d['studies']:
            self.doc.add_heading(study['short_citation'], 2)
            for exp in study['exps']:
                for ag in exp['ags']:
                    self.build_summary_table(ag)
