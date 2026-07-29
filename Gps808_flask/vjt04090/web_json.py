def flatten_json(data, parent=""):

    result = []


    if isinstance(data, dict):

        for key, value in data.items():

            name = (
                f"{parent}.{key}"
                if parent
                else key
            )


            result.extend(
                flatten_json(
                    value,
                    name
                )
            )


    elif isinstance(data, list):

        for i, value in enumerate(data):

            name = f"{parent}[{i}]"


            result.extend(
                flatten_json(
                    value,
                    name
                )
            )


    else:

        result.append(
            (
                parent,
                data
            )
        )


    return result