from clearml import Task
import joblib
from pathlib import Path
from dotenv import load_dotenv
import os
import shutil
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def load_model_from_clearml(
    project_name: str,
    task_name: str,
    artifact_name: str,
    destination_dir: str,
    target_filename: str
):
    load_dotenv()

    api_host = os.getenv("CLEARML_API_HOST")
    web_host = os.getenv("CLEARML_WEB_HOST")
    files_host = os.getenv("CLEARML_FILES_HOST")
    access_key = os.getenv("CLEARML_ACCESS_KEY")
    secret_key = os.getenv("CLEARML_SECRET_KEY")

    if all([api_host, web_host, files_host, access_key, secret_key]):
        Task.set_credentials(
            api_host=api_host,
            web_host=web_host,
            files_host=files_host,
            key=access_key,
            secret=secret_key
        )
    target_path = Path(destination_dir) / target_filename
    Path(destination_dir).mkdir(parents=True, exist_ok=True)

    if target_path.exists():
        logger.info(f"[ClearML] Модель найдена по пути: {target_path.resolve()}")
        return "Модель найдена и загружена"

    task = Task.get_task(project_name=project_name, task_name=task_name)
    local_path = task.artifacts[artifact_name].get_local_copy()
    target_path = Path(destination_dir) / target_filename
    shutil.copy(local_path, target_path)

    logger.info(f"[ClearML] Модель успешно загружена в: {target_path.resolve()}")

    return joblib.load(target_path)

    # task = Task.get_task(project_name=project_name, task_name=task_name)
    # local_path = task.artifacts[artifact_name].get_local_copy()
    # destination_path = Path(destination_dir) / Path(local_path).name
    # shutil.copy(local_path, destination_path)
    # print(f"[ClearML] Модель успешно загружена в: {destination_path.resolve()}")
    # return joblib.load(destination_path)