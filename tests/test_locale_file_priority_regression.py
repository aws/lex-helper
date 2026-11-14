# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest

from lex_helper.core.message_manager import MessageManager


@pytest.mark.parametrize("directory", ["messages", "config"])
@pytest.mark.parametrize("locale", ["es_ES", "fr_FR"])
def test_locale_file_is_selected_before_default_fallback(monkeypatch, tmp_path, directory, locale):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("MESSAGES_YAML_PATH", raising=False)
    monkeypatch.setattr(MessageManager, "_messages", {})
    (tmp_path / "messages.yaml").write_text("greeting: fallback", encoding="utf-8")
    localized_dir = tmp_path / directory
    localized_dir.mkdir()
    (localized_dir / f"messages_{locale}.yaml").write_text(f"greeting: {locale}", encoding="utf-8")

    assert MessageManager.get_message("greeting", locale=locale) == locale


def test_explicit_custom_directory_still_overrides_standard_locations(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(MessageManager, "_messages", {})
    custom_dir = tmp_path / "override"
    custom_dir.mkdir()
    monkeypatch.setenv("MESSAGES_YAML_PATH", str(custom_dir))
    (custom_dir / "messages.yaml").write_text("greeting: custom", encoding="utf-8")
    (tmp_path / "messages_es_ES.yaml").write_text("greeting: standard", encoding="utf-8")
    assert MessageManager.get_message("greeting", locale="es_ES") == "custom"
