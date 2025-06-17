from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Create user groups with appropriate permissions'

    def handle(self, *args, **kwargs):
        # Full access group
        client_admin, _ = Group.objects.get_or_create(name='Client Admin')
        client_admin.permissions.set(Permission.objects.all())

        # Internal Admin group
        internal_admin, _ = Group.objects.get_or_create(name='Internal Admin')
        view_permissions = Permission.objects.filter(codename__startswith='view_')
        internal_admin.permissions.set(view_permissions)

        # Read-only group
        read_only, _ = Group.objects.get_or_create(name='Read Only')
        read_only.permissions.set(view_permissions)

        self.stdout.write(self.style.SUCCESS("✅ Groups created successfully."))
