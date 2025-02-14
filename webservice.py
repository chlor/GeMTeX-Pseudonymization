# Licensed to the Universität Leipzig, under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The Universität Leipzig Darmstadt
# licenses this file to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
import io
import json
import logging
import os
import time
import zipfile
from datetime import datetime, date

import pandas as pd
import pkg_resources
import requests
import streamlit as st
import toml
from pycaprio import Pycaprio

from ClinSurGen.ProjectManagement.FileUtils import read_dir
from ClinSurGen.ProjectManagement.INCEpTIONprojects import set_surrogates_in_inception_project
from ClinSurGen.QualityControl import run_quality_control_of_project


st.set_page_config(
    page_title="GeMTeX Surrogator",
    layout="wide",
    initial_sidebar_state=st.session_state.setdefault("sidebar_state", "expanded"),
)

if st.session_state.get("flag"):
    st.session_state.sidebar_state = st.session_state.flag
    del st.session_state.flag
    time.sleep(0.01)
    st.rerun()


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
log = logging.getLogger()


def startup():

    st.markdown(
        """

        <style>
        .block-container {
            padding-top: 0rem;
            padding-bottom: 5rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        </style>

        <style>
        div[data-testid="stHorizontalBlock"] {
            margin-top: 1rem;
            border: thick double #999999;
            box-shadow: 0px 0px 10px #999999;
        }
        </style>

        <style>
        section.main > div {max-width:95%}
        </style>
        """,
        unsafe_allow_html=True,
    )

    project_info = get_project_info()
    if project_info:
        current_version, package_name = project_info
        latest_version = check_package_version(current_version, package_name)
        if latest_version:
            st.sidebar.warning(
                f"A new version ({latest_version}) of {package_name} is available. "
                f"You are currently using version ({current_version}). Please update the package."
            )


def get_project_info():
    try:
        pyproject_path = os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")
        with open(pyproject_path, "r") as f:
            pyproject_data = toml.load(f)
        version = pyproject_data["project"].get("version")
        name = pyproject_data["project"].get("name")
        if version and name:
            return version, name
        return None
    except (FileNotFoundError, KeyError):
        return None


def check_package_version(current_version, package_name):
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
        if response.status_code == 200:
            latest_version = response.json()["info"]["version"]
            if pkg_resources.parse_version(
                current_version
            ) < pkg_resources.parse_version(latest_version):
                return latest_version
    except requests.RequestException:
        return None
    return None


def create_directory_in_home():
    """
    Creates a directory in the user's home directory for storing Inception reports imported over the API.
    """
    home_dir = os.path.expanduser("~")
    new_dir_path = os.path.join(home_dir, ".inception_reports")
    try:
        os.makedirs(new_dir_path)
        os.makedirs(os.path.join(new_dir_path, "projects"))
    except FileExistsError:
        pass


def set_sidebar_state(value):
    if st.session_state.sidebar_state == value:
        st.session_state.flag = value
        st.session_state.sidebar_state = (
            "expanded" if value == "collapsed" else "collapsed"
        )
    else:
        st.session_state.sidebar_state = value
    st.rerun()


def login_to_inception(api_url, username, password):
    """
    Logs in to the Inception API using the provided API URL, username, and password.

    Args:
        api_url (str): The URL of the Inception API.
        username (str): The username for authentication.
        password (str): The password for authentication.

    Returns:
        tuple: A tuple containing a boolean value indicating whether the login was successful and an instance of the Inception client.

    """
    if "http" not in api_url:
        api_url = f"http://{api_url}"
    button = st.sidebar.button("Login")
    if button:
        inception_client = Pycaprio(api_url, (username, password))
        try:
            inception_client.api.projects()
            st.sidebar.success("Login successful ✅")
            return True, inception_client
        except Exception:
            st.sidebar.error("Login unsuccessful ❌")
            return False, None
    return False, None


def select_method_to_handle_the_data():
    """
    Allows the user to select a method to import data for generating reports.
    derived from select_method_to_import_data()
    """

    method = st.sidebar.radio(
        "Choose your method to import data:",
        ("Manually", "API"),
        index=0
    )

    if method == "Manually":
        st.sidebar.write(
            "Please input the path to the folder containing the INCEpTION projects."
        )
        projects_folder = st.sidebar.text_input("Projects Folder:", value="")
        uploaded_files = st.sidebar.file_uploader("Or upload project files:", accept_multiple_files=True, type="zip")

#    elif method == "API":
#        projects_folder = f"{os.path.expanduser('~')}/.inception_reports/projects"
#        os.makedirs(os.path.dirname(projects_folder), exist_ok=True)
#        st.session_state["projects_folder"] = projects_folder
#        api_url = st.sidebar.text_input("Enter API URL:", "")
#        username = st.sidebar.text_input("Username:", "")
#        password = st.sidebar.text_input("Password:", type="password", value="")
#        inception_status = st.session_state.get("inception_status", False)
#        inception_client = st.session_state.get("inception_client", None)
#        if not inception_status:
#            inception_status, inception_client = login_to_inception(
#                api_url, username, password
#            )
#            st.session_state["inception_status"] = inception_status
#            st.session_state["inception_client"] = inception_client
#
#        if inception_status and "available_projects" not in st.session_state:
#            inception_projects = inception_client.api.projects()
#            st.session_state["available_projects"] = inception_projects
#
#        if inception_status and "available_projects" in st.session_state:
#            st.sidebar.write("Select the projects to import:")
#            selected_projects = st.session_state.get("selected_projects", {})
#
#            for inception_project in st.session_state["available_projects"]:
#                project_name = inception_project.project_name
#                project_id = inception_project.project_id
#                selected_projects[project_id] = st.sidebar.checkbox(
#                    project_name, value=False
#                )
#                st.session_state["selected_projects"] = selected_projects
#
#            selected_projects_names = []
#            button = st.sidebar.button("Generate Reports")
#            if button:
#                for project_id, is_selected in selected_projects.items():
#                    if is_selected:
#                        project = inception_client.api.project(project_id)
#                        selected_projects_names.append(project.project_name)
#                        file_path = f"{projects_folder}/{project.project_name}.zip"
#                        st.sidebar.write(f"Importing project: {project.project_name}")
#                        log.info(
#                            f"Importing project {project.project_name} into {file_path} "
#                        )
#                        project_export = inception_client.api.export_project(
#                            project, "jsoncas"
#                        )
#                        with open(file_path, "wb") as f:
#                            f.write(project_export)
#                        log.debug("Import Success")
#
#                st.session_state["method"] = "API"
#                st.session_state["projects"] = read_dir(
#                    dir_path=projects_folder,
#                    selected_projects=selected_projects_names
#                )
#                set_sidebar_state("collapsed")

    #process_task = st.sidebar.radio(
    #    "Task:",
    #    (
    #            "Quality control",
    #            "Create surrogates"
    #    ),
    #    index=0
    #)

    #if process_task == "Quality control":

    button_qc = st.sidebar.button("Run Quality Control")
    button_sur = st.sidebar.button("Run Creation Surrogates")

    if button_qc:
        if uploaded_files:
            temp_dir = os.path.join(
                os.path.expanduser("~"), ".inception_reports", "temp_uploads"
            )

            os.makedirs(temp_dir, exist_ok=True)

            for uploaded_file in uploaded_files:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())

            selected_projects = [f.name.split(".")[0] for f in uploaded_files]

            st.session_state["projects"] = read_dir(temp_dir, selected_projects)
            st.session_state["projects_folder"] = temp_dir

        elif projects_folder:
            st.session_state["projects"] = read_dir(projects_folder)
            st.session_state["projects_folder"] = projects_folder

        st.session_state["method"] = "Manually"
        set_sidebar_state("collapsed")

    #elif process_task == "Create surrogates":


    if button_sur:

        # build config

        config = {
            'input': {
                'annotation_project_path': projects_folder,
                'task': 'surrogate'
            },
            'surrogate_process': {
                #'corpus_documents': corpus_documents,
                'surrogate_modes': []
            },
            'output': ''
            }

        # Do not remove the following code, we need it later!
        #if mode_x:
        #    config['surrogate_process']['surrogate_modes'].append("x")
        #if mode_entity:
        #    config['surrogate_process']['surrogate_modes'].append("entity")
        #if mode_gemtex:
        #    config['surrogate_process']['surrogate_modes'].append("gemtex")
        #if mode_fictive_names:
        #    config['surrogate_process']['surrogate_modes'].append("fictive_names")

        config['surrogate_process']['surrogate_modes'].append("gemtex")

        #config['surrogate_process']['date_normalization_to_cas'] = False
        #config['surrogate_process']['rename_files'] = rename_files
        config['surrogate_process']['rename_files'] = True

        #config['output'] = {'out_directory': 'output_gemtex_surrogator'}

        #if uploaded_files:
        #    temp_dir = os.path.join(
        #        os.path.expanduser("~"), ".inception_reports", "temp_uploads"
        #    )
        #
        #    os.makedirs(temp_dir, exist_ok=True)
        #
        #    for uploaded_file in uploaded_files:
        #        file_path = os.path.join(temp_dir, uploaded_file.name)
        #        with open(file_path, "wb") as f:
        #            f.write(uploaded_file.read())
        #
        #    selected_projects = [f.name.split(".")[0] for f in uploaded_files]
        #    st.session_state["projects"] = read_dir(temp_dir, selected_projects)
        #    st.session_state["projects_folder"] = temp_dir

        #elif projects_folder:
            #st.session_state["projects"] = read_dir(projects_folder)
        #st.session_state["projects_folder"] = projects_folder
        #st.session_state["corpus_documents"] = corpus_documents

        #st.sidebar.markdown('----') #file_formats = txt, xmi
        #file_format_txt = st.sidebar.checkbox("gemtex placeholders")
        #file_format_xmi = st.sidebar.checkbox("fictive names")

        st.session_state["config"] = config

        st.session_state["method"] = "Manually"
        set_sidebar_state("collapsed")


def find_element_by_name(element_list, name):
    """
    Finds an element in the given element list by its name.

    Args:
        element_list (list): A list of elements to search through.
        name (str): The name of the element to find.

    Returns:
        str: The UI name of the found element, or the last part of the name if not found.
    """
    for element in element_list:
        if element.name == name:
            return element.uiName
    return name.split(".")[-1]


def export_data(project_data):
    """
    Export project data to a JSON file, and store it in a directory named after the project and the current date.

    Parameters:
        project_data (dict): The data to be exported.
    """
    current_date = datetime.now().strftime("%Y_%m_%d")

    output_directory = os.getenv("INCEPTION_OUTPUT_DIR")

    if output_directory is None:
        output_directory = os.path.join(os.getcwd(), "exported_project_data")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    project_name = project_data["project_name"]

    with open(
        f"{output_directory}/{project_name.split('.')[0]}_{current_date}.json", "w"
    ) as output_file:
        json.dump(project_data, output_file, indent=4)
    st.success(
        f"{project_name.split('.')[0]} documents status exported successfully to {output_directory} ✅"
    )


def create_zip_download(wrong_annotations, stats_detailed, stats_detailed_cnt, corpus_files, project_name):
    """
    Create a zip file containing all generated JSON reports and provide a download button.
    """

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        dir_quality_control = 'quality_control'
        if not os.path.exists(dir_quality_control):
            os.makedirs(dir_quality_control)
        if not os.path.exists(dir_quality_control + os.sep + project_name):
            os.makedirs(dir_quality_control + os.sep + project_name)

        with open(file=dir_quality_control + os.sep + project_name + os.sep + project_name + '_report_wrong_annotations.json', mode='w', encoding='utf8') as outfile:
            json.dump(wrong_annotations, outfile, indent=2, sort_keys=False, ensure_ascii=True)

        json_data = json.dumps(wrong_annotations, indent=4)
        zip_file.writestr(
            zinfo_or_arcname=project_name + '_report_wrong_annotations.json',
            data=json_data
        )

        pd_corpus = pd.DataFrame(
            corpus_files,
            index=['part_of_corpus']
            ).rename_axis('document', axis=1).transpose()
        pd_corpus.to_csv(dir_quality_control + os.sep + project_name + os.sep + project_name + '_corpus_documents.csv')
        zip_file.writestr(
            zinfo_or_arcname=project_name + '_corpus_documents.csv',
            data=pd_corpus.to_csv(sep=',')
        )

        pd.DataFrame(stats_detailed).transpose().to_csv(dir_quality_control + os.sep + project_name + os.sep + project_name + '_corpus_details.csv')
        corpus_details = pd.DataFrame(stats_detailed).transpose().rename_axis('document', axis=1)

        pd.DataFrame(stats_detailed_cnt).transpose().to_csv(dir_quality_control + os.sep + project_name + '_statistics.csv')

        for item in ['OTHER', 'PROFESSION', 'LOCATION_OTHER', 'AGE']:
            if item in corpus_details.keys():
                df_corpus_details_item = pd.DataFrame(corpus_details).dropna(subset=[item])[item].transpose()
                df_corpus_details_item.to_csv(dir_quality_control + os.sep + project_name + os.sep + project_name + '_corpus_details_' + item + '.csv')
                zip_file.writestr(
                    zinfo_or_arcname=project_name + '_corpus_details_' + item + '.csv',
                    data=df_corpus_details_item.to_csv(sep=',')
                )

    zip_buffer.seek(0)

    st.download_button(
        label="Download Quality Control Reports (ZIP) - " + project_name,
        file_name="reports_quality_control_" + project_name + ".zip",
        mime="application/zip",
        data=zip_buffer.getvalue(),
    )


def main():

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

    startup()
    create_directory_in_home()

    st.write(
        "<style> h1 {text-align: center; margin-bottom: 50px, } </style>",
        unsafe_allow_html=True,
    )
    st.title("GeMTeX Surrogator for INCEpTION projects")
    st.write("<hr>", unsafe_allow_html=True)
    select_method_to_handle_the_data()

    generated_reports = []
    if "method" in st.session_state and "projects" in st.session_state:
        projects = [copy.deepcopy(project) for project in st.session_state["projects"]]
        projects = sorted(projects, key=lambda x: x["name"])
        for project in projects:
            wrong_annotations, stats_detailed, stats_detailed_cnt, corpus_files = run_quality_control_of_project(project)

            project_name = '-'.join(project['name'].replace('.zip', '').split('-')[0:-1])
            st.write('Project: ', project_name)
            create_zip_download(
                wrong_annotations=wrong_annotations,
                stats_detailed=stats_detailed,
                stats_detailed_cnt=stats_detailed_cnt,
                corpus_files=corpus_files,
                project_name=project_name
            )

            st.markdown('----')
            for file in wrong_annotations:
                st.write('file: ', file)
                st.write(pd.DataFrame(wrong_annotations[file]))

            st.markdown('----')
            st.markdown('Corpus files')
            st.write(pd.DataFrame(corpus_files, index=['part_of_corpus']).transpose())
            st.markdown('----')

        st.write("<hr>", unsafe_allow_html=True)
        #create_zip_download(generated_reports)

    if "config" in st.session_state:

        if not os.path.exists(st.session_state["config"]["output"]["out_directory"]):
            os.makedirs(st.session_state["config"]["output"]["out_directory"])

        #print(st.session_state["config"]["input"])
        #print(st.session_state["config"]["surrogate_process"])
        #print(st.session_state["config"]["output"])

        session_state = st.session_state["config"]

        st.write('Configuration')

        # CONFIG braucht in dem Zustand eigentlich nicht ausgegeben werden.
        #st.write(st.session_state["config"])
        set_surrogates_in_inception_project(config=st.session_state["config"])
        #st.write("<hr>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
