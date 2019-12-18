import os
import glob
import yaml

from singleton_decorator import singleton

from forum.models import Post

from populate.populator.manager import Manager
from .forum_builder import PostBuilder


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@singleton
class ForumManager(Manager):
    model = Post
    attribute = 'title'
    builder = PostBuilder
    files_path = '/files/'

    def get_object(self, value):
        data = self.load_file(value)
        obj = self.builder(data).create_object()
        self.output_success(obj, 'created!')
        return obj

    def load_file(self, value):
        path = '{base_dir}{file_path}'.format(
            base_dir=BASE_DIR, file_path=self.files_path)
        files = glob.glob(path + '**/{}.yml'.format(
            self.normalize(value)), recursive=True)
        f = files[0]
        file_obj = open(f)
        data = yaml.load(file_obj, Loader=yaml.Loader)
        file_obj.close()
        return data
