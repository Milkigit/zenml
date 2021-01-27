#  Copyright (c) maiot GmbH 2020. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.

import os
from typing import Dict, Text, List

from zenml.core.components.pusher import cortex_executor
from zenml.core.repo.repo import Repository
from zenml.core.steps.deployer.base_deployer import BaseDeployerStep
from zenml.utils.logger import get_logger
from zenml.utils.source_utils import get_path_from_source, \
    get_class_path_from_source

logger = get_logger(__name__)


class CortexDeployer(BaseDeployerStep):
    """
    Step class for deploying models using Cortex.
    """

    def __init__(self,
                 api_config: Dict,
                 predictor=None,
                 requirements: List = None,
                 conda_packages: List = None,
                 env: Text = 'aws',
                 force: bool = True,
                 wait: bool = False,
                 model_name: Text = '',
                 **kwargs):
        """
        Cortex Deployer Step constructor.

        Use this step to push your trained model to the
        [Cortex API](https://docs.cortex.dev/).

        Args:
            model_name: Name of the model.
            predictor: Cortex Predictor class.
            **kwargs: Additional keyword arguments.
        """
        if conda_packages is None:
            conda_packages = []
        if requirements is None:
            requirements = ['tensorflow==2.3.0']

        self.model_name = model_name
        self.env = env
        self.predictor = predictor
        self.api_config = api_config
        self.requirements = requirements
        self.conda_packages = conda_packages
        self.force = force
        self.wait = wait
        super(CortexDeployer, self).__init__(
            model_name=model_name,
            env=self.env,
            predictor=predictor,
            api_config=self.api_config,
            requirements=self.requirements,
            conda_packages=self.conda_packages,
            force=self.force,
            wait=self.wait,
            **kwargs)

    def get_config(self):
        predictor_path = self.predictor.__module__ + '.' + \
                         self.predictor.__name__
        p_file_path = \
            get_path_from_source(get_class_path_from_source(predictor_path))
        repo: Repository = Repository.get_instance()

        return {
            "cortex_serving_args": {
                "env": self.env,
                "api_config": self.api_config,
                "predictor_path": os.path.join(repo.path, p_file_path),
                "requirements": self.requirements,
                "conda_packages": self.conda_packages,
                "force": self.force,
                "wait": self.wait,
            }}

    def get_executor(self):
        return cortex_executor.Executor