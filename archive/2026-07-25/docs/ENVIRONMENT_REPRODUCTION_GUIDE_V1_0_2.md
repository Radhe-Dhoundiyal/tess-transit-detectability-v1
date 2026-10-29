# Environment reproduction guide v1.0.2

Python 3.12 is required. Create a virtual environment and install
`requirements-lock.txt`. Every selected pin is backed by installed
distribution metadata from the preserved execution environment. The lock is a
direct active-dependency lock, not a resolver-generated cross-platform
transitive lock. `requirements-dev.txt` covers active test/development imports;
`requirements-optional.txt` records optional workflows separately.

This recreates the verification environment only. Scientific reruns require
lawful reacquisition of excluded upstream data and separate authorization.
