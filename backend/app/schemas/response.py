"""Output contracts returned by the public API."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    environment: str


class ModelOption(BaseModel):
    id: str
    name: str


class ModelsResponse(BaseModel):
    models: list[ModelOption]


class OptionItem(BaseModel):
    id: str
    name: str


class OptionsResponse(BaseModel):
    difficulties: list[OptionItem]
    notes_formats: list[OptionItem]
    optional_sections: list[OptionItem]


class GeneratedNotesResponse(BaseModel):
    notes: str
    algorithm: str
    difficulty: str
    notes_format: str
