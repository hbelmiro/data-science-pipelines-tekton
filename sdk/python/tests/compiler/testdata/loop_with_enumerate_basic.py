# Copyright 2021 kubeflow.org
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

import kfp
from kfp import dsl
from kfp_tekton.compiler import TektonCompiler
from kfp_tekton.tekton import Loop


class Coder:
    def empty(self):
        return ""


TektonCompiler._get_unique_id_code = Coder.empty

produce_op = kfp.components.load_component_from_text('''\
name: Produce list
outputs:
- {name: data_list, type: List}
implementation:
  container:
    image: registry.access.redhat.com/ubi8/ubi-minimal
    command:
    - sh
    - -c
    - |
      echo "[1, 2, 3]" > "$0"
    - {outputPath: data_list}
''')

consume_op = kfp.components.load_component_from_text('''\
name: Consume data
inputs:
- {name: iter, type: Integer}
- {name: data, type: Integer}
implementation:
  container:
    image: registry.access.redhat.com/ubi8/ubi-minimal
    command:
    - echo
    - {inputValue: iter}
    - {inputValue: data}
''')


@dsl.pipeline(
    name='loop-with-enumerate-basic',
    description='Test pipeline to verify functions of par loop.'
)
def pipeline():
    source_task = produce_op()
    with Loop(source_task.outputs['data_list']).enumerate() as (i, item):
        consume_op(iter=i, data=item)


if __name__ == '__main__':
    from kfp_tekton.compiler import TektonCompiler
    compiler = TektonCompiler()
    compiler.compile(pipeline, __file__.replace('.py', '.yaml'))
    # compiler.tekton_inline_spec = False
    # compiler.compile(pipeline, __file__.replace('.py', '_noninlined.yaml'))
