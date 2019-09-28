
import argparse
from datetime import datetime as dt

parser = argparse.ArgumentParser()
parser.add_argument('datetime', help='Datetime to pass to the provided Kubeflow Pipeline')
parser.add_argument(
  '-t', '--timeout',
  default=60*60*24,
  type=int,
  help='Number of seconds to wait for pipeline to finish running'
)
args = parser.parse_args()
pipeline = 'pipeline.tar.gz'
fmt = '%Y%m%d-%H:%M:%S'
datetime = dt.strptime(args.datetime, fmt)
timeout = args.timeout

from kfp import Client
client = Client()

experiment_name = 'swf-%s' % pipeline
experiment = client.create_experiment(name=experiment_name)

datetime_str = datetime.strftime(fmt)
run = client.run_pipeline(
  experiment.id,
  '%s_%s' % (pipeline, datetime_str),
  pipeline,
  params={ 'datetime': datetime_str }
)

client.wait_for_run_completion(run.id, timeout=timeout)
