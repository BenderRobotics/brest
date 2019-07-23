from brest import Config

class Resources():
    '''
    Top level class for resource managing
    '''

    def __init__(self, project, config_path = None):
        self.resources = {}
        self.instantiate(project)

    def __getitem__(self, key):
        if key in self.resources:
            return self.resources[key]
        else:
            raise KeyError("Invali key: {}".format(key))

    def instantiate(self, project):
        # Tohle musí jít jinak
        from brest.supplies.supply_provider import SupplyProvider

        cfg = Config(project)
        res = []

        # Call all Providers here
        res.extend(SupplyProvider.construct_config(cfg))

        for r in res:
            self.resources[r.name] = r # 

if __name__ == "__main__":
    res = Resources('MMI')