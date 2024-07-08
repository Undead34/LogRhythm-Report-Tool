from .general import GeneralTemplate

class Templates():
    def __init__(self, report, queries, database, metadata, config) -> None:
        self.report, self.queries, self.db, self.metadata, self.config = report, queries, database, metadata, config

    def get_template(self, name):
        template = GeneralTemplate(self.report, self.queries, self.db, self.metadata, self.config)

        if name == "other": # example for some templates
            pass # Rempleze template here!

        template.run()

        return template
