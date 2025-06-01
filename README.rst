Credit for Tool Execution, JSON Schema
======================================

Sections
--------

1. **Who** ran this tool: ``affilitaion``
2. **What** tool was run: the ``tool_identifier``, ``tool_name``, ``tool_version``, ``tool_package_version``, along with the ``input_size``.
3. **Where** the tool was run: the ``infra`` stack, the physical ``location`` of the computer, the computer's ``cpu_identifier`` and ``cpu_mods``. Along with how many ``cpu_cores_assigned``.
4. **When** did this tool execution occur: ``start_time`` & ``stop_time``; or **how long** did the tool execution take, its ``duration``.
5. **What** was the result: ``final_output_size``, ``memory_used``, ``cpu_cores_used``, and ``number_of_cpu_cores_used``.


Testing
-------

.. code:: bash

  sudo apt-get install jsonschema-jv
  jv -output detailed execution_report.schema.json example.json
