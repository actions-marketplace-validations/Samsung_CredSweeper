import json
import os
import re
import subprocess
import sys
import tempfile
from typing import AnyStr, Tuple
from unittest import TestCase

import pytest

from tests import AZ_STRING, SAMPLES_POST_CRED_COUNT, SAMPLES_IN_DEEP_1, SAMPLES_IN_DEEP_3, SAMPLES_DIR, TESTS_DIR, PROJECT_DIR


class TestApp(TestCase):

    @staticmethod
    def _m_credsweeper(args) -> Tuple[AnyStr, AnyStr]:
        proc = subprocess.Popen(
            [sys.executable, "-m", "credsweeper", *args],  #
            cwd=PROJECT_DIR,  #
            stdout=subprocess.PIPE,  #
            stderr=subprocess.PIPE)  #
        return proc.communicate()

    def test_it_works_p(self) -> None:
        target_path = str(SAMPLES_DIR / "password")
        _stdout, _stderr = self._m_credsweeper(["--path", target_path, "--log", "silence"])
        output = " ".join(_stdout.decode("UTF-8").split()[:-1])

        expected = f"""
                    rule: Password
                    / severity: medium
                    / line_data_list:
                        [line: 'password = \"cackle!\"'
                        / line_num: 1
                        / path: {target_path}
                        / value: 'cackle!'
                        / entropy_validation: False]
                    / api_validation: NOT_AVAILABLE
                    / ml_validation: VALIDATED_KEY\n
                    Detected Credentials: 1\n
                    Time Elapsed:
                    """
        expected = " ".join(expected.split())
        assert output == expected

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_it_works_without_ml_p(self) -> None:
        target_path = str(SAMPLES_DIR / "password")
        _stdout, _stderr = self._m_credsweeper(["--path", target_path, "--ml_threshold", "0", "--log", "silence"])
        output = " ".join(_stdout.decode("UTF-8").split()[:-1])

        expected = f"""
                    rule: Password
                    / severity: medium
                    / line_data_list:
                        [line: 'password = \"cackle!\"'
                        / line_num: 1
                        / path: {target_path}
                        / value: 'cackle!'
                        / entropy_validation: False]
                    / api_validation: NOT_AVAILABLE
                    / ml_validation: NOT_AVAILABLE\n
                    Detected Credentials: 1\n
                    Time Elapsed:
                    """
        expected = " ".join(expected.split())
        assert output == expected

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_it_works_with_patch_p(self) -> None:
        target_path = str(SAMPLES_DIR / "password.patch")
        _stdout, _stderr = self._m_credsweeper(["--diff_path", target_path, "--log", "silence"])
        output = " ".join(_stdout.decode("UTF-8").split()[:-1])

        expected = """
                    rule: Password
                    / severity: medium
                    / line_data_list:
                    [line: '  "password": "dkajco1"'
                        / line_num: 3
                        / path: .changes/1.16.98.json
                        / value: 'dkajco1'
                        / entropy_validation: False]
                    / api_validation: NOT_AVAILABLE
                    / ml_validation: VALIDATED_KEY\n
                    Added File Credentials: 1\n
                    Deleted File Credentials: 0\n
                    Time Elapsed:
                    """
        expected = " ".join(expected.split())
        assert output == expected

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_it_works_with_multiline_in_patch_p(self) -> None:
        target_path = str(SAMPLES_DIR / "multiline.patch")
        _stdout, _stderr = self._m_credsweeper(["--diff_path", target_path, "--log", "silence"])
        output = " ".join(_stdout.decode("UTF-8").split()[:-1])

        expected = """
                    rule: AWS Client ID
                        / severity: high
                        / line_data_list:
                            [line: ' clid = "AKIAQWADE5R42RDZ4JEM"'
                            / line_num: 4
                            / path: creds.py
                            / value: 'AKIAQWADE5R42RDZ4JEM'
                            / entropy_validation: False]
                        / api_validation: NOT_AVAILABLE
                        / ml_validation: VALIDATED_KEY
                    rule: AWS Multi
                        / severity: high
                        / line_data_list:
                            [line: ' clid = "AKIAQWADE5R42RDZ4JEM"'
                            / line_num: 4
                            / path: creds.py
                            / value: 'AKIAQWADE5R42RDZ4JEM'
                            / entropy_validation: False, line: ' token = "V84C7sDU001tFFodKU95USNy97TkqXymnvsFmYhQ"'
                            / line_num: 5
                            / path: creds.py
                            / value: 'V84C7sDU001tFFodKU95USNy97TkqXymnvsFmYhQ'
                            / entropy_validation: True]
                        / api_validation: NOT_AVAILABLE
                        / ml_validation: VALIDATED_KEY
                    rule: Token
                        / severity: medium
                        / line_data_list:
                            [line: ' token = "V84C7sDU001tFFodKU95USNy97TkqXymnvsFmYhQ"'
                            / line_num: 5
                            / path: creds.py
                            / value: 'V84C7sDU001tFFodKU95USNy97TkqXymnvsFmYhQ'
                            / entropy_validation: True]
                        / api_validation: NOT_AVAILABLE
                        / ml_validation: VALIDATED_KEY\n
                    Added File Credentials: 3\n
                    Deleted File Credentials: 0\n
                    Time Elapsed:
                    """
        expected = " ".join(expected.split())
        assert output == expected

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @pytest.mark.api_validation
    def test_it_works_with_api_p(self) -> None:
        target_path = str(SAMPLES_DIR / "google_api_key")
        _stdout, _stderr = self._m_credsweeper(
            ["--path", target_path, "--ml_threshold", "0", "--api_validation", "--log", "silence"], )
        output = " ".join(_stdout.decode("UTF-8").split()[:-1])

        expected = f"""
                    rule: Google API Key
                    / severity: high
                    / line_data_list:
                    [line: 'AIzaGiReoGiCrackleCrackle12315618112315'
                        / line_num: 1
                        / path: {target_path}
                        / value: 'AIzaGiReoGiCrackleCrackle12315618112315'
                        / entropy_validation: True]
                    / api_validation: INVALID_KEY
                    / ml_validation: NOT_AVAILABLE\n
                    Detected Credentials: 1\n
                    Time Elapsed:
                    """
        expected = " ".join(expected.split())
        assert output == expected

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_it_works_n(self) -> None:
        _stdout, _stderr = self._m_credsweeper([])

        # Merge more than two whitespaces into one because _stdout and _stderr are changed based on the terminal size
        output = " ".join(_stderr.decode("UTF-8").split())

        expected = "usage: python -m credsweeper [-h]" \
                   " (--path PATH [PATH ...]" \
                   " | --diff_path PATH [PATH ...]" \
                   ")" \
                   " [--rules [PATH]]" \
                   " [--find-by-ext]" \
                   " [--depth POSITIVE_INT]" \
                   " [--ml_threshold FLOAT_OR_STR]" \
                   " [--ml_batch_size POSITIVE_INT]" \
                   " [--api_validation]" \
                   " [--jobs POSITIVE_INT]" \
                   " [--skip_ignored]" \
                   " [--save-json [PATH]]" \
                   " [--save-xlsx [PATH]]" \
                   " [--log LOG_LEVEL]" \
                   " [--size_limit SIZE_LIMIT]" \
                   " [--version] " \
                   "python -m credsweeper: error: one of the arguments" \
                   " --path" \
                   " --diff_path" \
                   " is required "
        expected = " ".join(expected.split())
        assert output == expected

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_log_p(self) -> None:
        apk_path = str(SAMPLES_DIR / "pem_key.apk")
        _stdout, _stderr = self._m_credsweeper(
            ["--log", "Debug", "--depth", "7", "--ml_threshold", "0", "--path", apk_path, "not_existed_path"])
        assert len(_stderr) == 0
        output = _stdout.decode()

        assert "DEBUG" in output, output
        assert "INFO" in output, output
        assert "WARNING" in output, output
        assert "ERROR" in output, output
        assert not ("CRITICAL" in output), output

        for line in output.splitlines():
            if 5 <= len(line) and "rule:" == line[0:5]:
                assert re.match(r"rule: \.*", line), line
            elif 21 <= len(line) and "Detected Credentials:" == line[0:21]:
                assert re.match(r"Detected Credentials: \d+", line), line
            elif 13 <= len(line) and "Time Elapsed:" == line[0:13]:
                assert re.match(r"Time Elapsed: \d+\.\d+", line), line
            else:
                assert re.match(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d+ \| (DEBUG|INFO|WARNING|ERROR) \| \w+ \| .*",
                                line), line

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_log_n(self) -> None:
        _stdout, _stderr = self._m_credsweeper(["--log", "CriTicaL", "--rule", "NOT_EXISTED_PATH", "--path", "."])
        assert len(_stderr) == 0
        output = _stdout.decode()

        assert not ("DEBUG" in output), output
        assert not ("INFO" in output), output
        assert not ("WARNING" in output), output
        assert not ("ERROR" in output), output
        assert "CRITICAL" in output, output

        assert any(
            re.match(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d+ \| (CRITICAL) \| \w+ \| .*", line)
            for line in output.splitlines()), output

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_help_p(self) -> None:
        _stdout, _stderr = self._m_credsweeper(["--help"])
        output = " ".join(_stdout.decode("UTF-8").split())
        help_path = os.path.join(TESTS_DIR, "..", "docs", "source", "guide.rst")
        with open(help_path, "r") as f:
            text = ""
            started = False
            for line in f.read().splitlines():
                if ".. note::" == line:
                    break
                if ".. code-block:: text" == line:
                    started = True
                    continue
                if started:
                    text += line
            expected = " ".join(text.split())
            assert output == expected

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_version_p(self) -> None:
        _stdout, stderr = self._m_credsweeper(["--version"])

        # Merge more than two whitespaces into one because _stdout and _stderr are changed based on the terminal size
        output = " ".join(_stdout.decode("UTF-8").split())

        assert re.match(r"CredSweeper \d+\.\d+\.\d+", output)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_patch_save_json_p(self) -> None:
        target_path = str(SAMPLES_DIR / "password.patch")
        with tempfile.TemporaryDirectory() as tmp_dir:
            json_filename = os.path.join(tmp_dir, "unittest_output.json")
            _stdout, _stderr = self._m_credsweeper(
                ["--diff_path", target_path, "--save-json", json_filename, "--log", "silence"])
            assert os.path.exists(os.path.join(tmp_dir, "unittest_output_added.json"))
            assert os.path.exists(os.path.join(tmp_dir, "unittest_output_deleted.json"))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_patch_save_json_n(self) -> None:
        target_path = str(SAMPLES_DIR / "password.patch")
        _stdout, _stderr = self._m_credsweeper(["--diff_path", target_path, "--log", "silence"])
        assert not os.path.exists(os.path.join(PROJECT_DIR, "unittest_output_added.json"))
        assert not os.path.exists(os.path.join(PROJECT_DIR, "unittest_output_deleted.json"))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_find_tests_p(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            json_filename = os.path.join(tmp_dir, "test_find_tests_p.json")
            assert os.path.exists(str(SAMPLES_DIR))
            assert os.path.isdir(str(SAMPLES_DIR))
            _stdout, _stderr = self._m_credsweeper(
                ["--path", str(SAMPLES_DIR), "--save-json", json_filename, "--log", "silence", "--jobs", "3"])
            assert os.path.exists(json_filename)
            with open(json_filename, "r") as json_file:
                report = json.load(json_file)
                # Fixed credentials number are found in samples
                assert len(report) == SAMPLES_POST_CRED_COUNT

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_find_by_ext_p(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            # .deR will be not found, only 4 of them
            for f in [".pem", ".crt", ".cer", ".csr", ".deR"]:
                file_path = os.path.join(tmp_dir, f"dummy{f}")
                assert not os.path.exists(file_path)
                open(file_path, "w").write(AZ_STRING)

            # not of all will be found due they are empty
            for f in [".jks", ".KeY"]:
                file_path = os.path.join(tmp_dir, f"dummy{f}")
                assert not os.path.exists(file_path)
                open(file_path, "w").close()

            # the directory hides all files
            ignored_dir = os.path.join(tmp_dir, "target")
            os.mkdir(ignored_dir)
            for f in [".pfx", ".p12"]:
                file_path = os.path.join(ignored_dir, f"dummy{f}")
                assert not os.path.exists(file_path)
                open(file_path, "w").write(AZ_STRING)

            json_filename = os.path.join(tmp_dir, "dummy.json")
            _stdout, _stderr = self._m_credsweeper(
                ["--path", tmp_dir, "--find-by-ext", "--save-json", json_filename, "--log", "silence"])
            assert os.path.exists(json_filename)
            with open(json_filename, "r") as json_file:
                report = json.load(json_file)
                assert len(report) == 4, f"{report}"
                for t in report:
                    assert t["line_data_list"][0]["line_num"] == -1
                    assert str(t["line_data_list"][0]["path"][-4:]) in [".pem", ".crt", ".cer", ".csr"]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_find_by_ext_n(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            for f in [".pem", ".crt", ".cer", ".csr", ".der", ".pfx", ".p12", ".key", ".jks"]:
                file_path = os.path.join(tmp_dir, f"dummy{f}")
                assert not os.path.exists(file_path)
                open(file_path, "w").write(AZ_STRING)
            json_filename = os.path.join(tmp_dir, "dummy.json")
            _stdout, _stderr = self._m_credsweeper(
                ["--path", tmp_dir, "--save-json", json_filename, "--log", "silence"])
            assert os.path.exists(json_filename)
            with open(json_filename, "r") as json_file:
                report = json.load(json_file)
                assert len(report) == 0

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_zip_p(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            json_filename = os.path.join(tmp_dir, "dummy.json")
            # depth = 3
            _stdout, _stderr = self._m_credsweeper(
                ["--log", "silence", "--path",
                 str(SAMPLES_DIR), "--save-json", json_filename, "--depth", "3"])
            assert os.path.exists(json_filename)
            with open(json_filename, "r") as json_file:
                report = json.load(json_file)
                assert len(report) == SAMPLES_POST_CRED_COUNT + SAMPLES_IN_DEEP_3
            # depth = 1
            _stdout, _stderr = self._m_credsweeper(
                ["--log", "silence", "--path",
                 str(SAMPLES_DIR), "--save-json", json_filename, "--depth", "1"])
            assert os.path.exists(json_filename)
            with open(json_filename, "r") as json_file:
                report = json.load(json_file)
                assert len(report) == SAMPLES_POST_CRED_COUNT + SAMPLES_IN_DEEP_1

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
