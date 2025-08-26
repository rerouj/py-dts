import os
import sys
from typing import Any

import pytest

from fastapi.testclient import TestClient
from pydantic import field_validator

from dts_api.settings.settings import get_settings
from pydantic_settings import BaseSettings, SettingsConfigDict

# Add the root directory to path to import your main app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your FastAPI app and settings dependencies
from main import app


class LocalSettings(BaseSettings):

    dts_context: str = None
    dts_version: str = None
    app_version: str = None
    root_collection: str = None
    storage: str = None
    indexer: str = None
    base_path: str = None
    metadata_path: str = None
    tei_ns: str = None
    testing: bool = None
    model_config = SettingsConfigDict(
        env_file="tests/dummy/.env.local"
    )

    @field_validator('base_path', mode='before')
    @classmethod
    def set_path(cls, value: Any):
        """
        Function to set the path for the tests
        :param value:
        :return:
        """
        if not os.path.isabs(value):
            return os.path.join(os.path.dirname(__file__), value)
        return value


class GithubSettings(BaseSettings):

    dts_context: str = None
    dts_version: str = None
    app_version: str = None
    root_collection: str = None
    storage: str = None
    indexer: str = None
    base_path: str = None
    metadata_path: str = None
    tei_ns: str = None
    model_config = SettingsConfigDict(
        env_file="tests/dummy/.env.github"
    )

@pytest.fixture(name='test_settings_fixture')
def test_settings_fixture():
    """
    Fixture to provide settings for the tests
    this fixture override settings used as a dependency in the app
    """

    def get_test_settings():
        """
        Function to get settings for the tests
        """
        return LocalSettings()

    return get_test_settings

@pytest.fixture(name='store_settings')
def store_settings_fixture(monkeypatch):
    """
    Fixture that override settings requested as a simple function outside dependencies
    principally called with the Store class
    :param monkeypatch:
    :return:
    """

    def get_patch_settings():
        """
        Function to get settings for the tests
        """
        return LocalSettings()

    monkeypatch.setattr("dts_api.classes.Store.get_settings", get_patch_settings)
    return get_patch_settings


@pytest.fixture(name='test_gh_settings_fixture')
def test_gh_settings_fixture():
    """
    Fixture to provide settings for the tests
    this fixture override settings used as a dependency in the app
    """

    def get_test_settings():
        """
        Function to get settings for the tests
        """
        return GithubSettings()

    return get_test_settings


@pytest.fixture(name='store_gh_settings')
def store_gh_settings_fixture(monkeypatch):
    """
    Fixture that override settings requested as a simple function outside dependencies
    principally called with the Store class
    :param monkeypatch:
    :return:
    """

    def get_patch_settings():
        """
        Function to get settings for the tests
        """
        return GithubSettings()

    monkeypatch.setattr("dts_api.classes.Store.get_settings", get_patch_settings)
    return get_patch_settings


@pytest.fixture(name="client")
def client(store_settings):
    app.dependency_overrides[get_settings] = store_settings

    with TestClient(app) as client:
        yield client

    app.dependency_overrides = {}