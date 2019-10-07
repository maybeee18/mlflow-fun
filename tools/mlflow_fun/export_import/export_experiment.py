""" 
Exports an experiment to a directory or zip file.
"""

import os
import mlflow
import shutil
import tempfile
from mlflow_fun.export_import import utils
from mlflow_fun.export_import.export_run import RunExporter
from mlflow_fun.common import mlflow_utils

class ExperimentExporter(object):
    def __init__(self, client=None, log_source_info=False, notebook_formats=["SOURCE"]):
        self.client = client or mlflow.tracking.MlflowClient()
        self.log_source_info = log_source_info
        self.notebook_formats = notebook_formats
        self.run_exporter = RunExporter(self.client, log_source_info, notebook_formats)

    def export_experiment(self, exp_id_or_name, output, log_source_info=False, notebook_formats=["SOURCE"]):
        exp = mlflow_utils.get_experiment(self.client, exp_id_or_name)
        exp_id = exp.experiment_id
        print("Exporting experiment '{}' (ID {}) to '{}'".format(exp.name,exp.experiment_id,output),flush=True)
        if output.endswith(".zip"):
            self.export_experiment_to_zip(exp_id, output, log_source_info)
        else:
            os.makedirs(output)
            self.export_experiment_to_dir(exp_id, output)

    def export_experiment_to_dir(self, exp_id, exp_dir):
        exp = self.client.get_experiment(exp_id)
        dct = {"experiment": utils.strip_underscores(exp)}
        infos = self.client.list_run_infos(exp_id)
        dct['export_info'] = { 'export_time': utils.get_now_nice(), 'num_runs': len(infos) }
        run_ids = []
        failed_run_ids = []
        for j,info in enumerate(infos):
            run_dir = os.path.join(exp_dir, info.run_id)
            print("Exporting run {}/{}: {}".format((j+1),len(infos),info.run_id),flush=True)
            res = self.run_exporter.export_run(info.run_id, run_dir)
            if res:
                run_ids.append(info.run_id)
            else:
                failed_run_ids.append(info.run_id)
        dct['run_ids'] = run_ids
        dct['failed_run_ids'] = failed_run_ids
        path = os.path.join(exp_dir,"manifest.json")
        utils.write_json_file(path, dct)
        if len(failed_run_ids) == 0:
            print("All {} runs succesfully exported".format(len(run_ids)))
        else:
            print("{}/{} runs succesfully exported".format(len(run_ids),len(infos)))
            print("{}/{} runs failed".format(len(failed_run_ids),len(infos)))

    def export_experiment_to_zip(self, exp_id, zip_file, log_source_info):
        temp_dir = tempfile.mkdtemp()
        try:
            self.export_experiment_to_dir(exp_id, temp_dir)
            utils.zip_directory(zip_file, temp_dir)
        finally:
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--experiment", dest="experiment", help="Source experiment ID or name", required=True)
    parser.add_argument("--output", dest="output", help="Output path", required=True)
    parser.add_argument("--log_source_info", dest="log_source_info", help="Set tags with import information", default=False, action='store_true')
    parser.add_argument("--notebook_formats", dest="notebook_formats", default="SOURCE", help="Notebook formats. Values are SOURCE, HTML, JUPYTER, DBC", required=False)
    args = parser.parse_args()
    print("Options:")
    for arg in vars(args):
        print("  {}: {}".format(arg,getattr(args, arg)))
    exporter = ExperimentExporter(None, args.log_source_info, utils.string_to_list(args.notebook_formats))
    exporter.export_experiment(args.experiment, args.output)
