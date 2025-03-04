"""
See http://py.cirun.io/api.html for cirun client docs
"""
import os
from functools import lru_cache
from typing import List, Dict, Any, Optional

from cirun import Cirun
from .github import gh_token, Github


@lru_cache
def get_cirun_installation_id(owner: str) -> int:
    # This ID needs a token with admin: org privileges.
    # Hard-code instead for easier use.
    if owner == "conda-forge":
        return 18453316
    else:
        gh = Github(gh_token)
        user = gh.get_user()
        if user.login == owner:
            user_or_org = user
        else:
            user_or_org = gh.get_organization(owner)
        for inst in user_or_org.get_installations:
            if inst.raw_data["app_slug"] == "cirun-application":
                return inst.app_id
        raise ValueError(f"cirun not found for owner {owner}")


def enable_cirun_for_project(owner: str, repo: str) -> Dict[str, Any]:
    """Enable the cirun.io Github Application for a particular repository."""
    print(f"Enabling cirun for {owner}/{repo} ...")
    cirun = _get_cirun_client()
    return cirun.set_repo(
        f"{owner}/{repo}", installation_id=get_cirun_installation_id(owner)
    )


def add_repo_to_cirun_resource(
    owner: str,
    repo: str,
    resource: str,
    cirun_policy_args: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Grant access to a cirun resource to a particular repository, with a particular policy."""
    cirun = _get_cirun_client()
    policy_args: Optional[Dict[str, Any]] = None
    if cirun_policy_args and "pull_request" in cirun_policy_args:
        policy_args = {"pull_request": True}
    print(
        f"Adding repo {owner}/{repo} to resource {resource} with policy_args: {policy_args}"
    )
    response = cirun.add_repo_to_resources(
        owner,
        repo,
        resources=[resource],
        teams=[repo],
        policy_args=policy_args,
    )
    print(f"response: {response} | {response.json().keys()}")
    return response


def remove_repo_from_cirun_resource(owner: str, repo: str, resource: str):
    """Revoke access to a cirun resource to a particular repository, with a particular policy."""
    cirun = _get_cirun_client()
    print(f"Removing repo {owner}/{repo} from resource {resource}.")
    response = cirun.remove_repo_from_resources(owner, repo, [resource])
    print(f"response: {response} | {response.json().keys()}")
    return response


@lru_cache
def _get_cirun_client() -> Cirun:
    try:
        return Cirun()
    except KeyError:
        raise RuntimeError(
            "You must have CIRUN_API_KEY defined to do Cirun CI registration. "
            "This requirement can be overriden by specifying `--without-cirun`"
        )
