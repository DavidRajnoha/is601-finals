## User Management System – Final Project Reflection

### Project Overview

The **User Management System** is an open-source platform initiated by Professor Keith Williams at NJIT. It aims to enhance student engagement with the software industry through events such as company tours, guest lectures, and mock interviews. The system is designed to foster practical learning by connecting students with industry professionals and providing real-world project experience.

This document outlines the features implemented, bugs fixed, and tests added during the development process, along with reflections on my contributions and learning outcomes.

---

### Developed Features

1. **[Feature: Refactor email flow to event-driven architecture using Celery and RabbitMQ](https://github.com/DavidRajnoha/is601-finals/issues/11)**

2. **[Feature: ]()**  
   _Description:_

---

### Fixed QA Issues

1. **[Hardcoded Repository Name in CI/CD Pipeline](https://github.com/DavidRajnoha/is601-finals/issues/1)**  
   Addressed hardcoded values that could break deployments across different environments.
2. **[Replace requirements.txt with Poetry for Dependency Management](https://github.com/DavidRajnoha/is601-finals/issues/2)**  
   Improved dependency management and consistency across development setups.
3. **[get_db dependency leads to only 500 status code responses](https://github.com/DavidRajnoha/is601-finals/issues/5)**  
   Resolved backend failure due to incorrect database session handling.
4. **[ID not present in verification email](https://github.com/DavidRajnoha/is601-finals/issues/8)**  
   Fixed missing dynamic user ID insertion in verification email template.
5. **[Retry Database Errors](https://github.com/DavidRajnoha/is601-finals/issues/16)
   Some Database errors can be retried and not cause the application to fail.
6. **[Refactor test suite to include unit tests alongside integration tests](https://github.com/DavidRajnoha/is601-finals/issues/12)**  
   Enhanced test coverage by separating unit and integration test responsibilities.

   
---

### Implemented Tests

1. **[Tests for Database Connections](https://github.com/DavidRajnoha/is601-finals/tree/main/tests/integration_tests/component/test_db)**
   5 tests
2. **[Tests testing the NGINX integration](https://github.com/DavidRajnoha/is601-finals/blob/main/tests/integration_tests/service/test_nginx/test_users_api.py)
   8 tests
3. **[Comprehensive refactor of the tests](https://github.com/DavidRajnoha/is601-finals/pull/18)
   Enables running majority of the tests locally without losing their functionality
4. Additional tests covering the features and QA issues
---

### DockerHub Repository

View the deployed project container:  
 [DockerHub Link Here](https://hub.docker.com/repository/docker/drajnoha/is601-finals)

---

### Personal Reflection

_Working on this final project provided deep insight into team collaboration, GitHub-driven development workflows, and the importance of test coverage and CI/CD practices. I particularly enjoyed learning about Celery and RabbitMQ for asynchronous processing, and this experience significantly boosted my confidence in backend development and system architecture._
