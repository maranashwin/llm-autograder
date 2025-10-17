# CS220 LLM Autograder

This repository contains tools and infrastructure for designing, building, and maintaining automated grading systems for CS220 (Data Science) projects using LLM-powered testing and Otter Grader integration.

## Overview

I wrote this repository for a course I was a Project Assistant/Head TA for. This repo contains comprehensive tools for creating data science projects with automated grading capabilities, including both public and hidden test generation using GPT-4.

## Key Features

- **LLM-Powered Mechanistic Testing**: Uses GPT-4 to generate comprehensive hidden test suites that verify code correctness through systematic evaluation rather than simple output comparison
- **Otter Grader Integration**: Seamless integration with Otter Grader for Gradescope autograder deployment
- **Data Pipeline Management**: Scripts for scraping and maintaining fresh datasets from reliable sources
- **Flexible Test Framework**: Support for various answer formats including DataFrames, lists, dictionaries, and more

## Sample Projects

This repository includes several sample projects that I designed and built the autograder for:

- **P4**: Pokemon data analysis project
- **P7**: Soccer statistics analysis
- **P10**: Exoplanet and star data analysis
- **P11**: Advanced exoplanet analysis with plotting

Each project demonstrates different aspects of data science workflows, from basic data manipulation to complex visualizations and statistical analysis.

## LLM-Powered Mechanistic Testing Approach

The core innovation of this system is its **mechanistic testing approach** rather than simple LLM-based code evaluation. Here's why this approach was necessary:

### The Problem with Traditional LLM Testing
Simply asking an LLM "Is this code correct?" is unreliable for educational assessment because:
- LLMs can be inconsistent in their evaluations
- They may miss subtle logical errors or edge cases
- Results can vary between different model versions or prompts
- Students could potentially game the system with clever prompting

### Our Mechanistic Solution
Instead, this system uses GPT-4 to **generate comprehensive test code** that mechanically verifies student solutions:

1. **Function Logic Testing**: Generates test inputs and compares student function outputs against reference implementations across multiple test cases
2. **Dependency Isolation**: When testing a function, replaces all dependencies with correct implementations to isolate the specific function being tested
3. **Rubric-Based Testing**: Each rubric point gets its own mechanistic test that verifies specific aspects of correctness (e.g., "uses required data structure", "handles edge cases correctly")
4. **Random Data Generation**: Creates fresh test datasets that follow the same format as real data but with different values to prevent hardcoding
5. **Comprehensive Coverage**: Tests not just final outputs but intermediate steps, variable assignments, and implementation choices

### Why This Approach Works
- **Deterministic**: Same test always produces same result
- **Comprehensive**: Tests multiple aspects of each solution
- **Scalable**: Can generate hundreds of test cases automatically
- **Educational**: Provides specific feedback about what went wrong
- **Robust**: Harder to game than simple output comparison

## Tools and Infrastructure

- **Project Design Workflow**: Complete pipeline from dataset identification to Gradescope deployment
- **Hidden Test Generation**: AI-powered creation of comprehensive mechanistic test suites
- **Data Generation Scripts**: Automated tools for creating fresh, realistic datasets
- **Rubric Management**: Detailed rubric systems with point allocation and feedback generation
- **Build System**: Automated project building and deployment tools

## Getting Started

See `instructions.md` for detailed setup instructions and project creation workflows. The repository includes comprehensive documentation for TAs, PMs, and Head TAs on how to use these tools effectively.

## Technology Stack

- Python with Jupyter Notebooks
- Otter Grader for automated grading
- GPT-4 API for intelligent test generation
- Various data science libraries (pandas, matplotlib, etc.)
- MongoDB for late day tracking
- Gradescope integration for assignment deployment
