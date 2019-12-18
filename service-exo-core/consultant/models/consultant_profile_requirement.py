class ConsultantProfileRequirement:
    KEY_PROFILE_PICTURE = 'profile-picture'
    KEY_KEYWORDS = 'keywords'
    KEY_SUMMARY = 'summary'
    KEY_LOCATION = 'location'
    KEY_LANGUAGES = 'languages'
    COMPLETE_VALUE = True

    def complete_profile_picture(self, consultant):
        self.complete(self.KEY_PROFILE_PICTURE, consultant)

    def complete_keywords(self, consultant):
        self.complete(self.KEY_KEYWORDS, consultant)

    def complete_summary(self, consultant):
        self.complete(self.KEY_SUMMARY, consultant)

    def complete_location(self, consultant):
        self.complete(self.KEY_LOCATION, consultant)

    def complete_languages(self, consultant):
        self.complete(self.KEY_LANGUAGES, consultant)

    def complete(self, key_name, consultant):
        key_value = self.COMPLETE_VALUE
        return self.set_consultant_requirement(key_name, consultant, key_value)

    def get_consultant_requirement(self, key_name, consultant):
        cache = consultant.get_cache_by_pk()
        return cache.get_key_value(consultant, key_name)

    def set_consultant_requirement(self, key_name, consultant, key_value):
        cache = consultant.get_cache_by_pk()
        return cache.set_key_value(consultant, key_name, key_value)
