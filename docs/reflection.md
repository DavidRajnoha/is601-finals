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

5. **[Refactor test suite to include unit tests alongside integration tests](https://github.com/DavidRajnoha/is601-finals/issues/12)**  
   Enhanced test coverage by separating unit and integration test responsibilities.

---

### Implemented Tests

1. **[Test: ]()**  
2. **[Test: ]()**  
3. **[Test: ]()**  
4. **[Test: ]()**  
5. **[Test: ]()**  
6. **[Test: ]()**  
7. **[Test: ]()**  
8. **[Test: ]()**  
9. **[Test: ]()**  
10. **[Test: ]()**

---

### DockerHub Repository

View the deployed project container:  
🔗 [DockerHub Link Here]()

---

### Personal Reflection

_Working on this final project provided deep insight into team collaboration, GitHub-driven development workflows, and the importance of test coverage and CI/CD practices. I particularly enjoyed learning about Celery and RabbitMQ for asynchronous processing, and this experience significantly boosted my confidence in backend development and system architecture._
