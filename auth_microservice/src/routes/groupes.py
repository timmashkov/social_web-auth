from uuid import UUID

from fastapi import APIRouter, Depends

from models import Group
from schemas.group import GroupOut, GroupSearchById, GroupSearchByTitle, GroupIn
from services.groups import GroupService

group_router = APIRouter(prefix="/groups")

GROUPS = Depends(GroupService)


@group_router.get("/all", response_model=list[GroupOut])
async def show_all_groups(group_repo: GroupService = GROUPS) -> list[Group]:
    return await group_repo.get_all_groups()


@group_router.get("/by_id/{group_id}", response_model=GroupOut)
async def show_all_groups(
    group_id: UUID, group_repo: GroupService = GROUPS
) -> GroupOut:
    return await group_repo.search_group_by_id(cmd=GroupSearchById(id=group_id))


@group_router.get("/by_title/{group_title}", response_model=GroupOut)
async def show_all_groups(
    group_title: str, group_repo: GroupService = GROUPS
) -> GroupOut:
    return await group_repo.search_group_by_title(
        cmd=GroupSearchByTitle(title=group_title)
    )


@group_router.post("/create", response_model=GroupOut)
async def register_group(cmd: GroupIn, group_repo: GroupService = GROUPS) -> GroupOut:
    return await group_repo.register_group(cmd=cmd)


@group_router.patch("/edit/{group_id}", response_model=GroupOut)
async def edit_group(
    group_id: UUID, cmd: GroupIn, group_repo: GroupService = GROUPS
) -> GroupOut:
    return await group_repo.edit_group(cmd=cmd, group_id=GroupSearchById(id=group_id))


@group_router.delete("/delete/{group_id}", response_model=GroupOut)
async def del_group(group_id: UUID, group_repo: GroupService = GROUPS) -> GroupOut:
    return await group_repo.drop_group(cmd=GroupSearchById(id=group_id))
