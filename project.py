#!/usr/bin/env python3

from pathlib import Path
import subprocess

from file_finder import find_projects
# from math_eval import evaluate_math

from rofl.router import RofiRouter
from rofl.response import RofiResponse, RofiResponseOptions, RofiRow
from rofl.request import RofiRequest, RofiRequestType

ROUTER = RofiRouter.from_environment()


def open_selected_terminal(path: Path) -> None:
    """Open the selected project in a new Kitty window."""

    if not path.is_dir():
        return

    subprocess.Popen(
        ["kitty", "--directory", str(path)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def open_selected_nvim(path: Path) -> None:
    if not path.is_dir():
        return

    subprocess.Popen(
        [
            "kitty",
            "--directory",
            str(path),
            "nvim",
            ".",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def create_project() -> RofiResponse:
    projects = find_projects()

    rows = [
        RofiRow(
            prj.name,
            display=prj.name.capitalize(),
            icon=["folder"],
            meta=str(prj.parent),
            info=str(prj),
        )
        for prj in projects
    ]

    rofi = RofiResponse(
        rows=rows,
        options=RofiResponseOptions("Projects", no_custom=False, use_hot_keys=True),
    )

    return rofi


# def handle_math(expr: str) -> None:
#     try:
#         result = evaluate_math(expr)
#     except (SyntaxError, ValueError, ZeroDivisionError) as exc:
#         response = RofiResponse(
#             rows=[
#                 RofiRow(
#                     value="math-error",
#                     display=f"Error: {exc}",
#                     nonselectable=True,
#                     permanent=True,
#                 ),
#             ],
#             options=RofiResponseOptions(
#                 prompt="Math",
#                 keep_filter=True,
#             ),
#         )
#
#         ROUTER.write(response.render())
#         return
#
#     response = RofiResponse(
#         rows=[
#             RofiRow(
#                 str(result),
#                 display=f"= {result}",
#                 info=str(result),
#             ),
#         ],
#         options=RofiResponseOptions(
#             "Maths",
#             keep_filter=True,
#             no_custom=False,
#         ),
#     )
#
#     ROUTER.write(response.render())
#

@ROUTER.bind(RofiRequestType.SELECTED)
def handle_selected(request: RofiRequest) -> None:
    if request.info is None:
        return
    p = Path(request.info)
    open_selected_terminal(p)
    return


@ROUTER.bind_custom(1)
def handle_nvim(request: RofiRequest) -> None:
    if request.info is None:
        return
    p = Path(request.info)
    open_selected_nvim(p)
    return


@ROUTER.bind_fb()
def fallback(request: RofiRequest) -> None:
    pstr = create_project().render()
    ROUTER.write(pstr)
    return


# @ROUTER.bind(RofiRequestType.CUSTOM_INPUT)
# def handle_custom(request: RofiRequest) -> None:
#     if request.input_text is None:
#         return
#
#     value = request.input_text.strip()
#
#     # if value.startswith("m "):
#     #     handle_math(value[2:])
#     #     return
#

def main():
    ROUTER.run()


if __name__ == "__main__":
    main()
