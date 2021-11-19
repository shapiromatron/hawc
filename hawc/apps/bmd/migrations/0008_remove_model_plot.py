from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("bmd", "0007_selected_units")]
    operations = [migrations.RemoveField(model_name="model", name="plot")]
