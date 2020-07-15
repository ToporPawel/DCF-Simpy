class Color:

    counter = 0
    colors = [
        "\033[30m",
        "\033[32m",
        "\033[31m",
        "\033[33m",
        "\033[34m",
        "\033[35m",
        "\033[36m",
        "\033[37m",
    ]
    normal = "\033[0m"


def get_color():
    color = Color.colors[Color.counter % len(Color.colors)]
    Color.counter += 1
    return color


def get_normal():
    return Color.normal
