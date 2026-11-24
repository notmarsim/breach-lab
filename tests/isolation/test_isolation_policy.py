"""Fail-closed isolation policy tests."""

from orchestrator.config import get_project_root
from validation.isolation import IsolationValidator


def test_repo_compose_passes_isolation() -> None:
    validator = IsolationValidator(get_project_root())
    report = validator.validate_compose()
    assert report.passed is True
    assert report.violations == []


def test_rejects_privileged_container() -> None:
    validator = IsolationValidator(get_project_root())
    bad_compose = {
        "networks": {"database": {"internal": True}, "restricted": {"internal": True}, "management": {"internal": True}},
        "services": {"evil": {"image": "ubuntu:24.04", "privileged": True}},
    }
    report = validator.validate_compose(bad_compose)
    assert report.passed is False
    assert any("privileged" in v for v in report.violations)


def test_rejects_docker_socket_mount() -> None:
    validator = IsolationValidator(get_project_root())
    bad_compose = {
        "networks": {"database": {"internal": True}, "restricted": {"internal": True}, "management": {"internal": True}},
        "services": {"evil": {"image": "ubuntu:24.04", "volumes": ["/var/run/docker.sock:/var/run/docker.sock"]}},
    }
    report = validator.validate_compose(bad_compose)
    assert report.passed is False
    assert any("Docker socket" in v for v in report.violations)


def test_rejects_host_network_and_public_bind() -> None:
    validator = IsolationValidator(get_project_root())
    bad_compose = {
        "networks": {"database": {"internal": False}, "restricted": {"internal": True}, "management": {"internal": True}},
        "services": {
            "evil": {
                "image": "ubuntu:24.04",
                "network_mode": "host",
                "ports": ["0.0.0.0:8080:80"],
            }
        },
    }
    report = validator.validate_compose(bad_compose)
    assert report.passed is False
    assert len(report.violations) >= 3
