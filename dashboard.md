# Dashboard Documentation

## Outline

- [Introduction](#introduction)

- [I. Dashboard](#i-dashboard)
  - [1. Dashboard Overview](#1-dashboard-overview)
  - [2. Directory Structure](#2-directory-structure)

- [II. Deployment](#ii-deployment)
  - [1. Deployment Process](#1-deployment-process)
  - [2. Hosting on Streamlit Community Cloud](#2-hosting-on-streamlit-community-cloud)
  - [3. Workflow: Copying to FA-Dashboard](#3-workflow-copying-to-fa-dashboard)
  - [4. Maintenance and Updates](#4-maintenance-and-updates)
  - [5. Troubleshooting and FAQ](#5-troubleshooting-and-faq)

## Introduction

This documentation provides a comprehensive guide to the Dashboard component of the FinApprenticeship project. It covers both the functionality of the Dashboard itself and the processes involved in deploying and maintaining it.

---

## I. Dashboard

### 1. Dashboard Overview

The Dashboard, located in the `Dashboard` directory, serves as the user interface for visualizing and interacting with key data and analytics within the FinApprenticeship ecosystem. Built with Streamlit, it offers an interactive and user-friendly experience designed to facilitate data-driven decision making.

---

### 2. Directory Structure

The `Dashboard` directory contains all source files required for the Dashboard's operation. This includes Streamlit scripts, configuration files, and supporting resources. Understanding this structure is essential for development and debugging.

---

## II. Deployment

### 1. Deployment Process

The deployment workflow involves copying the contents of the `Dashboard` directory to a separate GitHub repository named `FA-Dashboard`. This allows for a clear separation between the main project and the dashboard deployment, streamlining updates and releases.

---

### 2. Hosting on Streamlit Community Cloud

The Dashboard is hosted publicly via the Streamlit Community Cloud, which directly connects to the `FA-Dashboard` repository. Streamlit automatically detects code changes and redeploys the app, providing a seamless hosting and update experience.

---

### 3. Workflow: Copying to FA-Dashboard

A dedicated GitHub Actions workflow automates the process of copying files from the `Dashboard` directory to the `FA-Dashboard` repository. This ensures that the latest changes are always reflected in the deployed dashboard with minimal manual intervention.

---

### 4. Maintenance and Updates

To update the Dashboard, developers make changes within the `Dashboard` directory and trigger the workflow. Regular maintenance involves monitoring workflow runs, updating dependencies, and reviewing Streamlit logs for any errors.

---

### 5. Troubleshooting and FAQ

This section addresses common issues encountered during development, deployment, or usage of the Dashboard, and provides solutions or references to further support resources.
