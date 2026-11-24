# Contributing to BreachLab

Thank you for contributing to BreachLab! Please follow these guidelines to keep the platform modular, safe, reproducible, and maintainable.

## Development Principles
1. **Incremental & Verifiable**: Every PR or phase must leave the repository runnable and passing all tests.
2. **No Hardcoded Spoilers**: Never embed vulnerability names, exploit buttons, or solutions inside target UIs. Keep educational metadata in `vulnerability_catalog/` and walkthroughs in `walkthroughs/`.
3. **Strict Isolation**: Every new container service must pass `breachlab isolation-check`:
   - No `privileged: true`
   - No `/var/run/docker.sock` mount
   - No `network_mode: host`, `pid: host`, or `ipc: host`
   - Explicit CPU and memory limits
   - Defined health check
4. **No External Dependencies**: Target environments must function completely offline once base images are pulled/built.
5. **Honest Status Tracking**: Update `IMPLEMENTATION_STATUS.md` accurately after implementing and testing any component.

## Running Tests
```bash
pytest
```
