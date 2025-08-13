import argparse
import os
import sys
from datetime import date
import logging


if __name__ == '__main__':

    if not os.path.isdir('log'):
        os.mkdir('log')

    parser = argparse.ArgumentParser(
        description="GeMTeX Surrogator (Pseudonymization)"
    )

    # tasks
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-qc",
        "--quality_control",
        help="Quality control",
        action="store_true",
    )
    group.add_argument(
        "-x",
        "--x_surrogates",
        help="Create X Surrogates",
        action="store_true",
    )
    group.add_argument(
        "-e",
        "--entity_surrogates",
        help="Create entity Surrogates",
        action="store_true",
    )
    group.add_argument(
        "-g",
        "--gemtex_surrogates",
        help="Create GeMTeX Surrogates",
        action="store_true",
    )
    group.add_argument(
        "-f",
        "--fictive_surrogates",
        help="Create fictive Surrogates",
        action="store_true",
    )
    group.add_argument(
        "-ws",
        "--webservice",
        help="Starting via Webservice",
        action="store_true",
        )

    args_input = parser._action_groups.pop()
    parser.add_argument(
        "-p",
        "--INPUT_PATH",
        type=str,
        help='Path of input'
    )

    parser._action_groups.append(args_input)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(
                filename='log' + os.sep + 'logs_GeMTeX_Surrogator_' + str(date.today()) + '.log'
            ),
            logging.StreamHandler()
        ]
    )

    if args.webservice:
        from streamlit.web import cli
        sys.argv = [
            "streamlit",
            "run",
            f"{os.path.dirname(os.path.realpath(__file__))}" + os.sep + "GeMTeXSurrogator" + os.sep + "Webservice" + os.sep + "__init__.py",
        ]
        sys.exit(cli.main())

    else:
        if args.INPUT_PATH:

            if args.quality_control:
                from GeMTeXSurrogator.QualityControl import run_quality_control_only
                config = {
                    "input": {
                        "task": "quality_control",
                        "annotation_project_path": args.projects
                    }
                }
                run_quality_control_only(config=config)

            else:
                if args.x_surrogates:
                    surrogate_mode = "x"

                elif args.entity_surrogates:
                    surrogate_mode = "entity"

                elif args.gemtex_surrogates:
                    surrogate_mode = "gemtex"

                elif args.fictive_surrogates:
                    surrogate_mode = "fictive"

                else:
                    print('Wrong surrogation mode.')
                    exit(-1)

                json_files = []
                proc_inception_project = False

                for file_name in os.listdir(args.INPUT_PATH):
                    if file_name.endswith('json'):  # or file_name.endswith('xmi'):
                        json_files.append(args.INPUT_PATH + os.sep + file_name)
                    if file_name.endswith('zip'):
                        proc_inception_project = True

                config = {
                    "input": {
                        "task": "surrogate",
                        "annotation_project_path": args.INPUT_PATH,
                    },
                    "surrogate_process":
                        {
                            "surrogate_modes": surrogate_mode
                            # "date_surrogation": args.date
                        }
                }

                if json_files:
                    from GeMTeXSurrogator.Substitution.ProjectManagement import set_surrogates_in_inception_files
                    set_surrogates_in_inception_files(config=config)

                if proc_inception_project:
                    from GeMTeXSurrogator.Substitution.ProjectManagement import set_surrogates_in_inception_projects
                    set_surrogates_in_inception_projects(config=config)

        else:
            print('No projects specified.')
            exit(1)
