# Dashboard Documentation

## Outline

1. **Introduction**
2. **Dashboard Overview**
3. **Directory Structure**
4. **Deployment Process**
5. **Hosting on Streamlit Community Cloud**
6. **Workflow: Copying to FA-Dashboard**
7. **Maintenance and Updates**
8. **Troubleshooting and FAQ**

---

### 1. Introduction

This documentation provides a comprehensive guide to the Dashboard component of the FinApprenticeship project. It covers both the functionality of the Dashboard itself and the processes involved in deploying and maintaining it.

---

### 2. Dashboard Overview

The Dashboard, located in the `Dashboard` directory, serves as the user interface for visualizing and interacting with key data and analytics within the FinApprenticeship ecosystem. Built with Streamlit, it offers an interactive and user-friendly experience designed to facilitate data-driven decision making.

---

### 3. Directory Structure

The `Dashboard` directory contains all source files required for the Dashboard's operation. This includes Streamlit scripts, configuration files, and supporting resources. Understanding this structure is essential for development and debugging.

---

### 4. Deployment Process

The deployment workflow involves copying the contents of the `Dashboard` directory to a separate GitHub repository named `FA-Dashboard`. This allows for a clear separation between the main project and the dashboard deployment, streamlining updates and releases.

---

### 5. Hosting on Streamlit Community Cloud

The Dashboard is hosted publicly via the Streamlit Community Cloud, which directly connects to the `FA-Dashboard` repository. Streamlit automatically detects code changes and redeploys the app, providing a seamless hosting and update experience.

---

### 6. Workflow: Copying to FA-Dashboard

A dedicated GitHub Actions workflow automates the process of copying files from the `Dashboard` directory to the `FA-Dashboard` repository. This ensures that the latest changes are always reflected in the deployed dashboard with minimal manual intervention.

---

### 7. Maintenance and Updates

To update the Dashboard, developers make changes within the `Dashboard` directory and trigger the workflow. Regular maintenance involves monitoring workflow runs, updating dependencies, and reviewing Streamlit logs for any errors.

---

### 8. Troubleshooting and FAQ

This section addresses common issues encountered during development, deployment, or usage of the Dashboard, and provides solutions or references to further support resources.
