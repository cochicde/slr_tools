import yaml

from query.controller.dict import query_from_dict


def query_from_yaml(file: str):
    with open(file, encoding="utf-8") as yaml_file:
        try:
            data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            if hasattr(exc, "problem_mark"):
                mark = exc.problem_mark
                raise Exception(
                    "Error position: (%s:%s)", (mark.line + 1, mark.column + 1)
                )
    return query_from_dict(data)
