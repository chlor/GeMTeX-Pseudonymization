import argparse
import os
import sys
from datetime import date
import logging


if __name__ == '__main__':

    if not os.path.isdir('log'):
        os.mkdir('log')

    parser = argparse.ArgumentParser(
        description="GeMTeX Pseudonymization"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-qc",
        "--quality_control",
        help="Quality control",
        action="store_true",
        )
    group.add_argument(
        "-s",
        "--surrogate",
        help="Surrogate",
        action="store_true",
        )
    group.add_argument(
        "-ws",
        "--webservice",
        help="Starting via Webservice",
        action="store_true",
        )

    optional = parser._action_groups.pop()
    parser.add_argument(
        "-p",
        "--projects",
        type=str,
        help='Path to the input file'
    )

    parser._action_groups.append(optional)
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

    if args.quality_control:

        if not args.projects:
            print('No projects specified.')
            exit(1)

        from ClinSurGen.QualityControl import run_quality_control_only
        config = {
            "input": {
                "task": "quality_control",
                "annotation_project_path": args.projects
            }
        }
        run_quality_control_only(config=config)

    if args.surrogate:

        if not args.projects:
            print('No projects specified.')
            exit(1)

        from ClinSurGen.Substitution.ProjectManagement import set_surrogates_in_inception_projects
        config = {
            "input": {
                "task": "surrogate",
                "annotation_project_path": args.projects
            },
            "surrogate_process":
                {
                    "surrogate_modes": "gemtex"
                }
        }
        set_surrogates_in_inception_projects(config=config)

    if args.webservice:
        from streamlit.web import cli
        sys.argv = [
            "streamlit",
            "run",
            f"{os.path.dirname(os.path.realpath(__file__))}" + os.sep + "ClinSurGen" + os.sep + "Webservice" + os.sep + "__init__.py",
        ]
        sys.exit(cli.main())
