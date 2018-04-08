import shutil
import tempfile

from django.http import HttpResponse
from django.views.generic import View
from django.core.files.storage import get_storage_class
from django.core.files.base import File, ContentFile

from . import leases


class MultipartUploadView(View):
    temp_storage_class = None
    final_storage_class = None
    lease_manager_class = leases.LeaseManager

    def get_filename(self):
        return self.request.POST['filename']

    def get_temp_storage_class(self):
        klass = self.temp_storage_class or get_storage_class()
        return klass

    def get_temp_storage(self):
        self.temp_storage = self.get_temp_storage_class()()
        return self.temp_storage

    def get_final_storage_class(self):
        klass = self.final_storage_class or get_storage_class()
        return klass

    def get_final_storage(self):
        self.final_storage = self.get_final_storage_class()()
        return self.final_storage

    def get_lease_manager(self):
        self.lease_manager = self.lease_manager_class()
        return self.lease_manager

    def get_lease_id(self):
        return self.request.META['headers']['lease_id']

    def get_lease(self, lease_id=None):
        lease_id = lease_id or self.get_lease_id()
        lease_manager = self.get_lease_manager()
        return lease_manager.get_lease(lease_id)


class InitiateUploadView(MultipartUploadView):
    def post(self, *args, **kwargs):
        filename = self.get_filename()
        lease_manager = self.get_lease_manager()
        lease_id = lease_manager.create_lease(filename)
        return HttpResponse(lease_id)


class UploadPartView(MultipartUploadView):
    def put(self, *args, **kwargs):
        lease_id = self.get_lease_id()
        part_number = int(self.request.META['headers']['part_number'])
        lease_manager = self.get_lease_manager()
        lease = lease_manager.register_part(lease_id=lease_id,
                                            part_number=part_number)
        # Receive part
        part = ContentFile(self.request.body)
        part_filename = '%s-%s' % (lease['filename'], part_number)
        temp_storage = self.get_temp_storage()
        temp_storage.save(name=part_filename, content=part)
        lease = lease_manager.register_part_done(lease_id=lease_id,
                                                 part_number=part_number)
        return HttpResponse(lease_id)


class CompleteUploadView(MultipartUploadView):
    def post(self, *args, **kwargs):
        lease_id = self.get_lease_id()
        lease_manager = self.get_lease_manager()
        lease = lease_manager.completed_lease(lease_id=lease_id)
        temp_storage = self.get_temp_storage()
        final_file = tempfile.SpooledTemporaryFile()
        # Merge parts
        for part_number in sorted(lease['parts']):
            part_filename = '%s-%s' % (lease['filename'], part_number)
            part_file = temp_storage.open(part_filename)
            shutil.copyfileobj(part_file, final_file)
        final_file.seek(0)
        # Store final file
        final_storage = self.get_final_storage()
        final_storage.save(lease['filename'], final_file)
        # Delete parts files
        for part_number in lease['parts']:
            part_filename = '%s-%s' % (lease['filename'], part_number)
            part_file = temp_storage.delete(part_filename)
        lease_manager.uploaded_lease(lease_id)
        return HttpResponse(lease_id)


class AbortUploadView(MultipartUploadView):
    def delete(self, *args, **kwargs):
        lease_id = self.get_lease_id()
        temp_storage = self.get_temp_storage()
        lease_manager = self.get_lease_manager()
        lease = lease_manager.aborted_lease(lease_id=lease_id)
        # Delete parts files
        for part_number in lease['parts']:
            part_filename = '%s-%s' % (lease['filename'], part_number)
            part_file = temp_storage.delete(part_filename)
        return HttpResponse(lease_id)


class ListPartsView(MultipartUploadView):
    def get(self, *args, **kwargs):
        lease = self.get_lease()
        parts = str(lease['parts'])
        return HttpResponse(parts)


class ListUploadView(MultipartUploadView):
    pass


initiate_upload = InitiateUploadView.as_view()
upload_part = UploadPartView.as_view()
complete_upload = CompleteUploadView.as_view()
abort_upload = AbortUploadView.as_view()
list_parts = ListPartsView.as_view()
list_uploads = ListUploadView.as_view()
