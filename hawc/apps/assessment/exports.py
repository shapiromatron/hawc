from hawc.apps.common.helper import FlatFileExporter


class ValuesCompleteList(FlatFileExporter):
    def _get_header_row(self):
        return super()._get_header_row()
