from logging import getLogger

from anyblok import Declarations
from anyblok.column import (
    UUID,
    String,
    Selection
)
from anyblok.relationship import Many2One
from anyblok.field import Function
from anyblok_postgres.column import Jsonb


logger = getLogger(__name__)
Model = Declarations.Model
Mixin = Declarations.Mixin

from typing import Any

import importlib


def dynamic_import(class_path: str) -> Any:
    module, class_name = class_path.split(":")
    return getattr(importlib.import_module(module), class_name)

@Declarations.register(Declarations.Model)
class IOT:
    """Namespace for IOT"""


@Declarations.register(Declarations.Model.IOT)
class Device(Mixin.UuidColumn):
    name: str = String(label="Name", nullable=False)
    code: str = String(label="Code", unique=True, nullable=False)
    serialyzer_class: str = String(
        label="class used to serialyze state",
        nullable=False,
    )

    @property
    def serialyzer(self):
        return dynamic_import(self.serialyzer_class)


@Declarations.register(Declarations.Model.IOT)
class DesiredState(Mixin.UuidColumn, Mixin.TrackModel):
    
    device = Many2One(
        label="Devie",
        model=Declarations.Model.IOT.Device,
        one2many='desired_states',
        nullable=False
    )
    state = Jsonb(
        label="state",
        nullable=False,
    )


@Declarations.register(Declarations.Model.IOT)
class State(Mixin.UuidColumn, Mixin.TrackModel):

    device = Many2One(
        label="Devie",
        model=Declarations.Model.IOT.Device,
        one2many='states',
        nullable=False
    )
    state = Jsonb(
        label="state",
        nullable=False,
    )