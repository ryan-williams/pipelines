# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import unittest
import os

from kfp_component.google.dataflow import launch_template

MODULE = 'kfp_component.google.dataflow._launch_template'

@mock.patch('kfp_component.google.dataflow._common_ops.display')
@mock.patch(MODULE + '.KfpExecutionContext')
@mock.patch(MODULE + '.DataflowClient')
class LaunchTemplateTest(unittest.TestCase):

    def test_launch_template_succeed(self, mock_client, mock_context, mock_display):
        mock_context().__enter__().context_id.return_value = 'context-1'
        mock_client().list_aggregated_jobs.return_value = {
            'jobs': []
        }
        mock_client().launch_template.return_value = {
            'job': { 'id': 'job-1' }
        }
        expected_job = {
            'id': 'job-1',
            'currentState': 'JOB_STATE_DONE'
        }
        mock_client().get_job.return_value = expected_job

        result = launch_template('project-1', 'gs://foo/bar', {
            "parameters": {
                "foo": "bar"
            },
            "environment": {
                "zone": "us-central1"
            }
        })

        self.assertEqual(expected_job, result)
        mock_client().launch_template.assert_called_once()

    def test_launch_template_retry_succeed(self, 
        mock_client, mock_context, mock_display):
        mock_context().__enter__().context_id.return_value = 'ctx-1'
        # The job with same name already exists.
        mock_client().list_aggregated_jobs.return_value = {
            'jobs': [{
                'id': 'job-1',
                'name': 'test_job-ctx-1'
            }]
        }
        pending_job = {
            'currentState': 'JOB_STATE_PENDING'
        }
        expected_job = {
            'id': 'job-1',
            'currentState': 'JOB_STATE_DONE'
        }
        mock_client().get_job.side_effect = [pending_job, expected_job]

        result = launch_template('project-1', 'gs://foo/bar', {
            "parameters": {
                "foo": "bar"
            },
            "environment": {
                "zone": "us-central1"
            }
        }, job_name_prefix='test-job', wait_interval=0)

        self.assertEqual(expected_job, result)
        mock_client().launch_template.assert_not_called()
    
    def test_launch_template_fail(self, mock_client, mock_context, mock_display):
        mock_context().__enter__().context_id.return_value = 'context-1'
        mock_client().list_aggregated_jobs.return_value = {
            'jobs': []
        }
        mock_client().launch_template.return_value = {
            'job': { 'id': 'job-1' }
        }
        failed_job = {
            'id': 'job-1',
            'currentState': 'JOB_STATE_FAILED'
        }
        mock_client().get_job.return_value = failed_job

        self.assertRaises(RuntimeError, 
            lambda: launch_template('project-1', 'gs://foo/bar', {
                "parameters": {
                    "foo": "bar"
                },
                "environment": {
                    "zone": "us-central1"
                }
            }))

    