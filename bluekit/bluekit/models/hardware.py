
class Hadrware():
    def __init__(self, details):
        self.name = details["name"]
        self.description = details["description"]
        self.setup_verification = details['setup_verification']
        self.working_directory = details['working_directory']
        self.bt_version_min = details['bt_version_min']
        self.bt_version_max = details['bt_version_max']
        self.needs_setup_verification = details['needs_setup_verification']
    
    def check_setup():
        return True




