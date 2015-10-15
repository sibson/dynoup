from dynoup import ma
from scaler.models import Check, App


class CheckSchema(ma.Schema):
    id = ma.UUID(dump_only=True)
    app_id = ma.UUID(dump_only=True)
    name = ma.Str(dump_only=True)
    dynotype = ma.Str(dump_only=True)

    class Meta:
        model = Check
        fields = ('url', 'params')


class AppSchema(ma.ModelSchema):
    class Meta:
        model = App
        fields = ('id', 'name', 'checks')
