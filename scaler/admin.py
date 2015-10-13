from flask_admin.contrib.sqla import ModelView


class UserAdmin(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_exclude_list = ['htoken']  # -1 blacklisting


class AppAdmin(ModelView):
    can_create = False
    can_edit = False
    can_delete = False


class CheckAdmin(ModelView):
    pass
