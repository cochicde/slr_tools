import yaml

class Parameters:
    __ALL_PARAMETERS = {}
    GLOBAL_PARAMETERS = {}

    @staticmethod
    def initialize(yaml_file: str):
        Parameters.__ALL_PARAMETERS = dict(
            (cl.NAME, {}) for cl in Parameters.__subclasses__()
        )
        Parameters.GLOBAL_PARAMETERS = {}

        with open(yaml_file) as config:
            yaml_config = yaml.load(config, Loader=yaml.FullLoader)

            class Object(object):
                pass

            args = Object()
            for key, value in yaml_config["config"].items():
                if key == "parameter":
                    for provider_name, provider_value in value.items():
                        for argument_name, argument_value in provider_value.items():
                            Parameters.__ALL_PARAMETERS[provider_name][argument_name] = argument_value

                else:
                    Parameters.GLOBAL_PARAMETERS[key] = value


    def get_parameters(name: str) -> dict:
        return Parameters.__ALL_PARAMETERS.get(name, {})
