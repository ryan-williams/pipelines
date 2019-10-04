
import argparse
from datetime import datetime as dt
from kfp import Client
from tempfile import NamedTemporaryFile


parser = argparse.ArgumentParser()
parser.add_argument('--pipeline_yaml', help='Kubeflow Pipeline specification (in YAML format) to run')
parser.add_argument('--datetime', required=False, help='Datetime to pass to the provided Kubeflow Pipeline')
parser.add_argument('--name', help='Name of this pipeline, for use in experiment and run names')
parser.add_argument(
  '-t', '--timeout',
  default=60*60*24,
  type=int,
  help='Number of seconds to wait for pipeline to finish running'
)

args = parser.parse_args()

fmt = '%Y-%m-%dT%H:%M:%SZ'
if args.datetime:
  datetime_str = args.datetime
  datetime = dt.strptime(args.datetime, fmt)
else:
  datetime = dt.now()
  datetime_str = datetime.strftime(fmt)

pipeline_yaml = args.pipeline_yaml
name = args.name
timeout = args.timeout

with NamedTemporaryFile(suffix='pipeline.yaml') as f:
  f.write(pipeline_yaml.encode())
  pipeline_path = f.name

  client = Client()

  experiment_name = 'swf-%s' % name
  experiment = client.create_experiment(name=experiment_name)

  run = client.run_pipeline(
    experiment.id,
    '%s_%s' % (name, datetime_str),
    pipeline_path,
  )

client.wait_for_run_completion(run.id, timeout=timeout)
