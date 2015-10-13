from flask_admin.contrib.sqla import ModelView


from dynoup import db, admin

from scaler import models


class UserAdmin(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_exclude_list = ['htoken']  # -1 blacklisting
admin.add_view(UserAdmin(models.User, db.session))


class AppAdmin(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
admin.add_view(AppAdmin(models.App, db.session))


class CheckAdmin(ModelView):
    pass
admin.add_view(CheckAdmin(models.Check, db.session))
