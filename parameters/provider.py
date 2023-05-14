class Provider:
    __ALL_PARAMETERS = {}

    def initialize(parameters: list[str]):
        if parameters is None:
            return

        Provider.__ALL_PARAMETERS = dict(
            (cl.NAME, {}) for cl in Provider.__subclasses__()
        )

        if Provider.__ALL_PARAMETERS == {}:
            return

        for parameter in parameters:
            if "." not in parameter or "=" not in parameter:
                raise Exception("Invalid parameter " + parameter)

            parser, name_value = parameter.split(".")
            name, value = name_value.split("=")

            if parser not in Provider.__ALL_PARAMETERS:
                raise Exception("Parser name unknown: " + parser)

            Provider.__ALL_PARAMETERS[parser][name] = value

    def get_parameters(name: str) -> dict:
        return Provider.__ALL_PARAMETERS.get(name, {})
