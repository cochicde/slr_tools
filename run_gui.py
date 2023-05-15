import argparse
from parameters.provider import Provider
from gui.application import ApplicationGUI
import yaml


def main():
    parser = argparse.ArgumentParser(prog="Filter Papers GUI Tool")

    parser.add_argument(
        "-c", "--config", help="Configuration yaml file", default="config-gui.yml"
    )

    args = parser.parse_args()

    with open(args.config) as config:
        yaml_config = yaml.load(config, Loader=yaml.FullLoader)

        class Object(object):
            pass

        args = Object()
        for key, value in yaml_config["config"].items():
            if key == "parameter":
                values = []

                for provider_name, provider_value in value.items():
                    for argument_name, argument_value in provider_value.items():
                        values.append(
                            provider_name
                            + "."
                            + argument_name
                            + "="
                            + str(argument_value)
                        )

                args.__setattr__(key, values)
                continue

            args.__setattr__(key, value)

    # initilize global parameter provider
    Provider.initialize(args.parameter)

    app = ApplicationGUI(args.database)
    app.launch()
    return


if __name__ == "__main__":
    main()
