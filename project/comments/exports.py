from utils.helper import FlatFileExporter


class CommentExporterComplete(FlatFileExporter):

    def _get_header_row(self):
        header = [
            "Type",
            "Name",
            "Title",
            "Text",
            "Commenter",
            "Date"
        ]
        return header

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            rows.append([
                unicode(obj.content_object),
                unicode(obj.content_object._meta.object_name),
                obj.title,
                obj.text,
                obj.commenter.get_full_name(),
                obj.last_updated
            ])
        return rows

