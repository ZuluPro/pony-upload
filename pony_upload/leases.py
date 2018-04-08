from uuid import uuid4
from django.core.cache import cache
from . import settings


class LeaseNotFound(Exception):
    pass


class LeaseManager(object):
    def create_lease(self, filename):
        lease_id = uuid4()
        lease = {'filename': filename, 'parts': {}}
        cache.set(lease_id, lease, settings.LEASE_TIMEOUT)
        return lease_id

    def get_lease(self, lease_id):
        lease = cache.get(lease_id, None)
        if lease is None:
            msg = 'Lease %s not found.' % lease_id
            raise LeaseNotFound(msg)
        return lease

    def register_part(self, lease_id, part_number):
        lease = self.get_lease(lease_id)
        lease['parts'][part_number] = 'registered'
        cache.set(lease_id, lease, settings.LEASE_TIMEOUT)
        return lease

    def register_part_done(self, lease_id, part_number):
        lease = self.get_lease(lease_id)
        lease['parts'][part_number] = 'received'
        cache.set(lease_id, lease, settings.LEASE_TIMEOUT)
        return lease

    def completed_lease(self, lease_id):
        lease = self.get_lease(lease_id)
        return lease

    def uploaded_lease(self, lease_id):
        cache.delete(lease_id)

    def uploaded_lease(self, lease_id):
        cache.delete(lease_id)
