class ERPDatabaseRouter:
    """Route Student, Faculty, and Admin models to their own databases.

    - `students` app → `students` database
    - `faculty` app  → `faculty` database
    - `accounts` app (custom User) → `admin` database
    - All other apps (e.g., `departments`) → default database
    """
    student_apps = {'students'}
    faculty_apps = {'faculty'}
    admin_apps = {'accounts'}  # accounts app holds the custom User model

    def db_for_read(self, model, **hints):
        return self._db_for_model(model)

    def db_for_write(self, model, **hints):
        return self._db_for_model(model)

    def _db_for_model(self, model):
        app_label = model._meta.app_label
        if app_label in self.student_apps:
            return 'students'
        if app_label in self.faculty_apps:
            return 'faculty'
        if app_label in self.admin_apps:
            return 'admin'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        db1 = self._db_for_model(obj1.__class__)
        db2 = self._db_for_model(obj2.__class__)
        # Allow cross‑database relation with accounts app (custom User)
        if obj1._meta.app_label == 'accounts' or obj2._meta.app_label == 'accounts':
            return True
        # Allow cross‑database relation between profiles and departments
        if obj1._meta.app_label == 'departments' or obj2._meta.app_label == 'departments':
            return True
        # Allow cross‑database relation between students and faculty (e.g., assignments)
        if obj1._meta.app_label == 'students' and obj2._meta.app_label == 'faculty':
            return True
        if obj1._meta.app_label == 'faculty' and obj2._meta.app_label == 'students':
            return True
        return db1 == db2

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.student_apps:
            return db == 'students'
        if app_label in self.faculty_apps:
            return db == 'faculty'
        if app_label in self.admin_apps:
            return db == 'admin'
        return db == 'default'
