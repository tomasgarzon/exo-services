import yaml


class CommandYAMLMixin:
    def load_file(self, filepath):
        with open(filepath, 'r') as stream:
            try:
                return yaml.load(stream, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                self.logger.error(exc)

    def find_tuple_values(self, tpl, values):
        """
        Allow to find a key which is related to a value in python tuple
        """
        return [str(obj[0]) for obj in tpl if obj[1] in values]
