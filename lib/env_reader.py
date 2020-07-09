class EnvReader:

    env_file = '.env'
    env_vars = []

    def __init__(self):
        self.read_env_file()

    def __del__(self):
        pass

    def read_env_file(self):
        with open(self.env_file) as f:
            for line in f:
                line=line.strip()
                if len(line)==0:
                    continue

                if line.startswith('#'):
                    continue

                key, value = line.strip().split('=', 1)
                self.env_vars.append({'name': key, 'value': value}) # Save to a list

        # print(self.env_vars);

    def getenv(self,var):
        try:
            val = [x for x in self.env_vars if x['name']==var]
            return val[0]['value']
        except Exception as e:
            return None