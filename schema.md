# Objects
* [`Infrastructure provider`](#reference-provider)
* [`Tool execution report`](#reference-tool-execution-report) (root object)


---------------------------------------
<a name="reference-provider"></a>
## Infrastructure provider

**`Infrastructure provider` Properties**

|   |Type|Description|Required|
|---|---|---|---|
|**infra_name**|`string`|Name of the infrastructure (who should get credit).| &#10003; Yes|
|**infra_identifier**|`string` `[1-*]`|Unique identifier for this infrastructure.| &#10003; Yes|
|**infra_version**|`string`|For software-based infrastructure: the version.|No|

Additional properties are allowed.

### provider.infra_name

Name of the infrastructure (who should get credit).

* **Type**: `string`
* **Required**:  &#10003; Yes

### provider.infra_identifier

Unique identifier for this infrastructure.

* **Type**: `string` `[1-*]`
* **Required**:  &#10003; Yes

### provider.infra_version

For software-based infrastructure: the version.

* **Type**: `string`
* **Required**: No




---------------------------------------
<a name="reference-tool-execution-report"></a>
## Tool execution report

Gives credit for the specific execution of a data analysis tool.

**`Tool execution report` Properties**

|   |Type|Description|Required|
|---|---|---|---|
|**report_format_version**|`any`|The version of the execution schema used.| &#10003; Yes|
|**affiliation**|`string` `[]`|Identifier of the project associated with this tool execution. Ideally from the Research Organization Registry (ROR) https://ror.org/.|No|
|**tool_identifier**|`string` `[1-*]`|Tool identifier from bio.tools, an RRID, or other source. Multiple identifiers can be supplied for tools known to multiple registries.| &#10003; Yes|
|**tool_name**|`string`|What the tool author calls the tool.| &#10003; Yes|
|**tool_version**|`string`|Version of the tool that was actually run, ideally captured from the tool itself or a packaging system (apt, conda, pip, etc..).|No|
|**tool_package_version**|`string`|Version of the tool as reported from a packaging system (apt, conda, pip, etc..).|No|
|**input_size**|`integer`|The total size of the inputs, MUST be (rounded or binned, details TBD).|No|
|**infra**|`provider` `[1-*]`|Physical and virtual infrastructure providers involved in the coordination, planning, and/or execution of this tool. Could be platforms, service providers, etc.| &#10003; Yes|
|**location**|`object`|Physical location where the computer was. Don't really care more than city/country.|No|
|**cpu_identifier**|`string`|For example, the 'model name' field from /proc/cpuinfo on Linux.|No|
|**cpu_mods**|`string`|For example, the 'bugs' field from /proc/cpuinfo on Linux.|No|
|**cpu_cores_assigned**|`integer`|Number of CPU cores that were assigned to the tool.|No|
|**start_time**|`string`|Time & date of the beginning of tool execution.|No|
|**end_time**|`string`|Time & date of the end of tool execution.|No|
|**duration**|`string`|Duration of tool execution. Using start_time & end_time is preferred.|No|
|**final_outputs_size**|`integer`|Disk usage (bytes), MUST be (rounded or binned, details TBD).|No|
|**memory_used**|`integer`|Peak memory usage, measured in bytes.|No|
|**cpu_cores_used**|`number`|Measured number of CPU cores used.|No|
|**gpu_cores_used**|`integer`|Measured number of GPU cores used.|No|

Additional properties are allowed.

### Tool execution report.report_format_version

The version of the execution schema used.

* **Type**: `any`
* **Required**:  &#10003; Yes
* **Allowed values**:
    * `0.0.1`

### Tool execution report.affiliation

Identifier of the project associated with this tool execution. Ideally from the Research Organization Registry (ROR) https://ror.org/.

* **Type**: `string` `[]`
* **Required**: No

### Tool execution report.tool_identifier

Tool identifier from bio.tools, an RRID, or other source. Multiple identifiers can be supplied for tools known to multiple registries.

* **Type**: `string` `[1-*]`
* **Required**:  &#10003; Yes

### Tool execution report.tool_name

What the tool author calls the tool.

* **Type**: `string`
* **Required**:  &#10003; Yes

### Tool execution report.tool_version

Version of the tool that was actually run, ideally captured from the tool itself or a packaging system (apt, conda, pip, etc..).

* **Type**: `string`
* **Required**: No

### Tool execution report.tool_package_version

Version of the tool as reported from a packaging system (apt, conda, pip, etc..).

* **Type**: `string`
* **Required**: No

### Tool execution report.input_size

The total size of the inputs, MUST be (rounded or binned, details TBD).

* **Type**: `integer`
* **Required**: No

### Tool execution report.infra

Physical and virtual infrastructure providers involved in the coordination, planning, and/or execution of this tool. Could be platforms, service providers, etc.

* **Type**: `provider` `[1-*]`
* **Required**:  &#10003; Yes

### Tool execution report.location

Physical location where the computer was. Don't really care more than city/country.

* **Type**: `object`
* **Required**: No

### Tool execution report.cpu_identifier

For example, the 'model name' field from /proc/cpuinfo on Linux.

* **Type**: `string`
* **Required**: No

### Tool execution report.cpu_mods

For example, the 'bugs' field from /proc/cpuinfo on Linux.

* **Type**: `string`
* **Required**: No

### Tool execution report.cpu_cores_assigned

Number of CPU cores that were assigned to the tool.

* **Type**: `integer`
* **Required**: No

### Tool execution report.start_time

Time & date of the beginning of tool execution.

* **Type**: `string`
* **Required**: No
* **Format**: date-time

### Tool execution report.end_time

Time & date of the end of tool execution.

* **Type**: `string`
* **Required**: No
* **Format**: date-time

### Tool execution report.duration

Duration of tool execution. Using start_time & end_time is preferred.

* **Type**: `string`
* **Required**: No
* **Format**: duration

### Tool execution report.final_outputs_size

Disk usage (bytes), MUST be (rounded or binned, details TBD).

* **Type**: `integer`
* **Required**: No

### Tool execution report.memory_used

Peak memory usage, measured in bytes.

* **Type**: `integer`
* **Required**: No
* **Minimum**: ` > 0`

### Tool execution report.cpu_cores_used

Measured number of CPU cores used.

* **Type**: `number`
* **Required**: No

### Tool execution report.gpu_cores_used

Measured number of GPU cores used.

* **Type**: `integer`
* **Required**: No


