# Auto generated from execution_report.linkml.yaml by pythongen.py version: 0.0.1
# Generation date: 2025-06-04T17:44:44
# Schema: execution_report
#
# id: https://elixir-europe.org/platforms/compute/execution_report.linkml.yaml
# description: Gives credit for the specific execution of a data analysis tool.
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import re
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union
)

from jsonasobj2 import (
    JsonObj,
    as_dict
)
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions
)
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import (
    camelcase,
    sfx,
    underscore
)
from linkml_runtime.utils.metamodelcore import (
    bnode,
    empty_dict,
    empty_list
)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str
)
from rdflib import (
    Namespace,
    URIRef
)

from linkml_runtime.linkml_model.types import Datetime, Integer, String, Uri
from linkml_runtime.utils.metamodelcore import URI, XSDDateTime

metamodel_version = "1.7.0"
version = "0.0.2"

# Namespaces
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
REPORT = CurieNamespace('report', 'https://w3id.example.com/execution_report#')
SCHEMA = CurieNamespace('schema', 'http://schema.org/')
DEFAULT_ = CurieNamespace('', 'https://elixir-europe.org/platforms/compute/execution_report.linkml.yaml/')


# Types

# Class references



@dataclass(repr=False)
class Provider(YAMLRoot):
    """
    Infrastructure provider.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("https://elixir-europe.org/platforms/compute/execution_report.linkml.yaml/Provider")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Provider"
    class_model_uri: ClassVar[URIRef] = URIRef("https://elixir-europe.org/platforms/compute/execution_report.linkml.yaml/Provider")

    infra_name: Optional[str] = None
    infra_identifier: Optional[Union[str, list[str]]] = empty_list()
    infra_version: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.infra_name is not None and not isinstance(self.infra_name, str):
            self.infra_name = str(self.infra_name)

        if not isinstance(self.infra_identifier, list):
            self.infra_identifier = [self.infra_identifier] if self.infra_identifier is not None else []
        self.infra_identifier = [v if isinstance(v, str) else str(v) for v in self.infra_identifier]

        if self.infra_version is not None and not isinstance(self.infra_version, str):
            self.infra_version = str(self.infra_version)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Address(YAMLRoot):
    """
    The name of the physical location where the computation took place.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["PostalAddress"]
    class_class_curie: ClassVar[str] = "schema:PostalAddress"
    class_name: ClassVar[str] = "Address"
    class_model_uri: ClassVar[URIRef] = URIRef("https://elixir-europe.org/platforms/compute/execution_report.linkml.yaml/Address")

    addressCountry: Optional[str] = None
    postalCode: Optional[str] = None
    addressRegion: Optional[str] = None
    addressLocality: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.addressCountry is not None and not isinstance(self.addressCountry, str):
            self.addressCountry = str(self.addressCountry)

        if self.postalCode is not None and not isinstance(self.postalCode, str):
            self.postalCode = str(self.postalCode)

        if self.addressRegion is not None and not isinstance(self.addressRegion, str):
            self.addressRegion = str(self.addressRegion)

        if self.addressLocality is not None and not isinstance(self.addressLocality, str):
            self.addressLocality = str(self.addressLocality)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Location(YAMLRoot):
    """
    Physical location where the computer was. Don't really care more than city/country.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["Place"]
    class_class_curie: ClassVar[str] = "schema:Place"
    class_name: ClassVar[str] = "Location"
    class_model_uri: ClassVar[URIRef] = URIRef("https://elixir-europe.org/platforms/compute/execution_report.linkml.yaml/Location")

    name: Optional[str] = None
    address: Optional[Union[dict, Address]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.address is not None and not isinstance(self.address, Address):
            self.address = Address(**as_dict(self.address))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Tool(YAMLRoot):
    """
    The data analysis tool that was executed, for which this tool execution report was generated about.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["SoftwareApplication"]
    class_class_curie: ClassVar[str] = "schema:SoftwareApplication"
    class_name: ClassVar[str] = "Tool"
    class_model_uri: ClassVar[URIRef] = URIRef("https://elixir-europe.org/platforms/compute/execution_report.linkml.yaml/Tool")

    name: Optional[str] = None
    identifier: Optional[Union[Union[str, URI], list[Union[str, URI]]]] = empty_list()
    version: Optional[str] = None
    package_version: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if not isinstance(self.identifier, list):
            self.identifier = [self.identifier] if self.identifier is not None else []
        self.identifier = [v if isinstance(v, URI) else URI(v) for v in self.identifier]

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if self.package_version is not None and not isinstance(self.package_version, str):
            self.package_version = str(self.package_version)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Report(YAMLRoot):
    """
    Tool execution report. Gives credit for the specific execution of a data analysis tool.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("https://elixir-europe.org/platforms/compute/execution_report.linkml.yaml/Report")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Report"
    class_model_uri: ClassVar[URIRef] = URIRef("https://elixir-europe.org/platforms/compute/execution_report.linkml.yaml/Report")

    report_format_version: Optional[str] = None
    affiliation: Optional[Union[str, list[str]]] = empty_list()
    tool: Optional[Union[dict, Tool]] = None
    input_size_bytes: Optional[int] = None
    infra: Optional[Union[Union[dict, Provider], list[Union[dict, Provider]]]] = empty_list()
    location: Optional[Union[dict, Location]] = None
    cpu_identifier: Optional[str] = None
    cpu_mods: Optional[str] = None
    cpu_cores_assigned: Optional[int] = None
    start_time: Optional[Union[str, XSDDateTime]] = None
    end_time: Optional[Union[str, XSDDateTime]] = None
    duration: Optional[str] = None
    final_outputs_size_bytes: Optional[int] = None
    memory_used: Optional[int] = None
    cpu_cores_used: Optional[int] = None
    gpu_cores_used: Optional[int] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.report_format_version is not None and not isinstance(self.report_format_version, str):
            self.report_format_version = str(self.report_format_version)

        if not isinstance(self.affiliation, list):
            self.affiliation = [self.affiliation] if self.affiliation is not None else []
        self.affiliation = [v if isinstance(v, str) else str(v) for v in self.affiliation]

        if self.tool is not None and not isinstance(self.tool, Tool):
            self.tool = Tool(**as_dict(self.tool))

        if self.input_size_bytes is not None and not isinstance(self.input_size_bytes, int):
            self.input_size_bytes = int(self.input_size_bytes)

        if not isinstance(self.infra, list):
            self.infra = [self.infra] if self.infra is not None else []
        self.infra = [v if isinstance(v, Provider) else Provider(**as_dict(v)) for v in self.infra]

        if self.location is not None and not isinstance(self.location, Location):
            self.location = Location(**as_dict(self.location))

        if self.cpu_identifier is not None and not isinstance(self.cpu_identifier, str):
            self.cpu_identifier = str(self.cpu_identifier)

        if self.cpu_mods is not None and not isinstance(self.cpu_mods, str):
            self.cpu_mods = str(self.cpu_mods)

        if self.cpu_cores_assigned is not None and not isinstance(self.cpu_cores_assigned, int):
            self.cpu_cores_assigned = int(self.cpu_cores_assigned)

        if self.start_time is not None and not isinstance(self.start_time, XSDDateTime):
            self.start_time = XSDDateTime(self.start_time)

        if self.end_time is not None and not isinstance(self.end_time, XSDDateTime):
            self.end_time = XSDDateTime(self.end_time)

        if self.duration is not None and not isinstance(self.duration, str):
            self.duration = str(self.duration)

        if self.final_outputs_size_bytes is not None and not isinstance(self.final_outputs_size_bytes, int):
            self.final_outputs_size_bytes = int(self.final_outputs_size_bytes)

        if self.memory_used is not None and not isinstance(self.memory_used, int):
            self.memory_used = int(self.memory_used)

        if self.cpu_cores_used is not None and not isinstance(self.cpu_cores_used, int):
            self.cpu_cores_used = int(self.cpu_cores_used)

        if self.gpu_cores_used is not None and not isinstance(self.gpu_cores_used, int):
            self.gpu_cores_used = int(self.gpu_cores_used)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.provider__infra_name = Slot(uri=DEFAULT_.infra_name, name="provider__infra_name", curie=DEFAULT_.curie('infra_name'),
                   model_uri=DEFAULT_.provider__infra_name, domain=None, range=Optional[str])

slots.provider__infra_identifier = Slot(uri=DEFAULT_.infra_identifier, name="provider__infra_identifier", curie=DEFAULT_.curie('infra_identifier'),
                   model_uri=DEFAULT_.provider__infra_identifier, domain=None, range=Optional[Union[str, list[str]]])

slots.provider__infra_version = Slot(uri=SCHEMA.softwareVersion, name="provider__infra_version", curie=SCHEMA.curie('softwareVersion'),
                   model_uri=DEFAULT_.provider__infra_version, domain=None, range=Optional[str])

slots.address__addressCountry = Slot(uri=SCHEMA.addressCountry, name="address__addressCountry", curie=SCHEMA.curie('addressCountry'),
                   model_uri=DEFAULT_.address__addressCountry, domain=None, range=Optional[str])

slots.address__postalCode = Slot(uri=SCHEMA.postalCode, name="address__postalCode", curie=SCHEMA.curie('postalCode'),
                   model_uri=DEFAULT_.address__postalCode, domain=None, range=Optional[str])

slots.address__addressRegion = Slot(uri=SCHEMA.addressRegion, name="address__addressRegion", curie=SCHEMA.curie('addressRegion'),
                   model_uri=DEFAULT_.address__addressRegion, domain=None, range=Optional[str])

slots.address__addressLocality = Slot(uri=SCHEMA.addressLocality, name="address__addressLocality", curie=SCHEMA.curie('addressLocality'),
                   model_uri=DEFAULT_.address__addressLocality, domain=None, range=Optional[str])

slots.location__name = Slot(uri=SCHEMA.name, name="location__name", curie=SCHEMA.curie('name'),
                   model_uri=DEFAULT_.location__name, domain=None, range=Optional[str])

slots.location__address = Slot(uri=DEFAULT_.address, name="location__address", curie=DEFAULT_.curie('address'),
                   model_uri=DEFAULT_.location__address, domain=None, range=Optional[Union[dict, Address]])

slots.tool__name = Slot(uri=SCHEMA.name, name="tool__name", curie=SCHEMA.curie('name'),
                   model_uri=DEFAULT_.tool__name, domain=None, range=Optional[str])

slots.tool__identifier = Slot(uri=SCHEMA.identifier, name="tool__identifier", curie=SCHEMA.curie('identifier'),
                   model_uri=DEFAULT_.tool__identifier, domain=None, range=Optional[Union[Union[str, URI], list[Union[str, URI]]]])

slots.tool__version = Slot(uri=SCHEMA.softwareVersion, name="tool__version", curie=SCHEMA.curie('softwareVersion'),
                   model_uri=DEFAULT_.tool__version, domain=None, range=Optional[str])

slots.tool__package_version = Slot(uri=DEFAULT_.package_version, name="tool__package_version", curie=DEFAULT_.curie('package_version'),
                   model_uri=DEFAULT_.tool__package_version, domain=None, range=Optional[str])

slots.report__report_format_version = Slot(uri=DEFAULT_.report_format_version, name="report__report_format_version", curie=DEFAULT_.curie('report_format_version'),
                   model_uri=DEFAULT_.report__report_format_version, domain=None, range=Optional[str],
                   pattern=re.compile(r'0.0.2'))

slots.report__affiliation = Slot(uri=SCHEMA.affiliation, name="report__affiliation", curie=SCHEMA.curie('affiliation'),
                   model_uri=DEFAULT_.report__affiliation, domain=None, range=Optional[Union[str, list[str]]])

slots.report__tool = Slot(uri=DEFAULT_.tool, name="report__tool", curie=DEFAULT_.curie('tool'),
                   model_uri=DEFAULT_.report__tool, domain=None, range=Optional[Union[dict, Tool]])

slots.report__input_size_bytes = Slot(uri=DEFAULT_.input_size_bytes, name="report__input_size_bytes", curie=DEFAULT_.curie('input_size_bytes'),
                   model_uri=DEFAULT_.report__input_size_bytes, domain=None, range=Optional[int])

slots.report__infra = Slot(uri=DEFAULT_.infra, name="report__infra", curie=DEFAULT_.curie('infra'),
                   model_uri=DEFAULT_.report__infra, domain=None, range=Optional[Union[Union[dict, Provider], list[Union[dict, Provider]]]])

slots.report__location = Slot(uri=DEFAULT_.location, name="report__location", curie=DEFAULT_.curie('location'),
                   model_uri=DEFAULT_.report__location, domain=None, range=Optional[Union[dict, Location]])

slots.report__cpu_identifier = Slot(uri=DEFAULT_.cpu_identifier, name="report__cpu_identifier", curie=DEFAULT_.curie('cpu_identifier'),
                   model_uri=DEFAULT_.report__cpu_identifier, domain=None, range=Optional[str])

slots.report__cpu_mods = Slot(uri=DEFAULT_.cpu_mods, name="report__cpu_mods", curie=DEFAULT_.curie('cpu_mods'),
                   model_uri=DEFAULT_.report__cpu_mods, domain=None, range=Optional[str])

slots.report__cpu_cores_assigned = Slot(uri=DEFAULT_.cpu_cores_assigned, name="report__cpu_cores_assigned", curie=DEFAULT_.curie('cpu_cores_assigned'),
                   model_uri=DEFAULT_.report__cpu_cores_assigned, domain=None, range=Optional[int])

slots.report__start_time = Slot(uri=SCHEMA.startTime, name="report__start_time", curie=SCHEMA.curie('startTime'),
                   model_uri=DEFAULT_.report__start_time, domain=None, range=Optional[Union[str, XSDDateTime]])

slots.report__end_time = Slot(uri=SCHEMA.endTime, name="report__end_time", curie=SCHEMA.curie('endTime'),
                   model_uri=DEFAULT_.report__end_time, domain=None, range=Optional[Union[str, XSDDateTime]])

slots.report__duration = Slot(uri=DEFAULT_.duration, name="report__duration", curie=DEFAULT_.curie('duration'),
                   model_uri=DEFAULT_.report__duration, domain=None, range=Optional[str])

slots.report__final_outputs_size_bytes = Slot(uri=DEFAULT_.final_outputs_size_bytes, name="report__final_outputs_size_bytes", curie=DEFAULT_.curie('final_outputs_size_bytes'),
                   model_uri=DEFAULT_.report__final_outputs_size_bytes, domain=None, range=Optional[int])

slots.report__memory_used = Slot(uri=DEFAULT_.memory_used, name="report__memory_used", curie=DEFAULT_.curie('memory_used'),
                   model_uri=DEFAULT_.report__memory_used, domain=None, range=Optional[int])

slots.report__cpu_cores_used = Slot(uri=DEFAULT_.cpu_cores_used, name="report__cpu_cores_used", curie=DEFAULT_.curie('cpu_cores_used'),
                   model_uri=DEFAULT_.report__cpu_cores_used, domain=None, range=Optional[int])

slots.report__gpu_cores_used = Slot(uri=DEFAULT_.gpu_cores_used, name="report__gpu_cores_used", curie=DEFAULT_.curie('gpu_cores_used'),
                   model_uri=DEFAULT_.report__gpu_cores_used, domain=None, range=Optional[int])
