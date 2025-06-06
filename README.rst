Credit for Tool Execution, JSON Schema
======================================

Posters from the ELIXIR All Hands 2025 meeting

- https://docs.google.com/presentation/d/1B2Xeb_BJuwEQxe2J05cmuM-Vtr07D7Eb8KbcyN0AwTw/edit?usp=drivesdk
- https://drive.google.com/file/d/1DTE1wgxKJNyzZos-m7YHrMHHh0vSZO2M/view?usp=drivesdk
- https://docs.google.com/presentation/d/1DaT4fq1OsLc5UJfj9m-stjpfIWFMla9dNp2TLVoTXgM/edit?usp=drivesdk

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
