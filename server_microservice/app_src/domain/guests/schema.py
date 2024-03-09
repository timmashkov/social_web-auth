from uuid import UUID

from pydantic import BaseModel, field_validator, model_validator

__all__ = ("GetGuestById", "GuestUpdate", "GuestIn", "GuestOut")


class GetGuestById(BaseModel):
    id: UUID


class GuestUpdate(BaseModel):
    first_name: str
    last_name: str

    @field_validator("first_name")
    def check_first_name(cls, data):
        if data.istitle():
            return data
        raise ValueError("First name must start from title letter")

    @field_validator("last_name")
    def check_first_name(cls, data):
        if data.istitle():
            return data
        raise ValueError("Last name must start from title letter")

    @model_validator(mode="before")
    def check_names(cls, values):
        if values.get("first_name") == values.get("last_name"):
            raise ValueError("First name can't be equal last name")
        return values


class GuestIn(GuestUpdate):
    event_id: UUID


class GuestOut(GuestIn, GetGuestById):
    pass
